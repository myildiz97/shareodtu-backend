from models.food_model.food_model import Food, UpdateFood, CreateFood
from services.users.user_services import get_current_user
from fastapi import Depends, HTTPException, Body
from models.user_model.user_model import UserType, User
import random
from datetime import datetime, timedelta
from models.food_model.food_model import CollectionCode
from typing import Annotated, Optional


async def create_food(
    food_data: Annotated[CreateFood, Body()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.user_type.value != UserType.VENDOR.value:
        raise HTTPException(
            status_code=403, detail="Only vendors can create food items"
        )

    # Check if the food already exists
    existing_food = await Food.find_one(
        {
            "food_type": food_data.food_type,
            "vendor.$id": current_user.id,
        }
    )
    if existing_food:
        raise HTTPException(status_code=400, detail="Food item already exists")

    food = Food(
        food_type=food_data.food_type,
        count=food_data.count,
        vendor=current_user,
    )

    try:
        await food.insert()
        return {"message": "Food created"}
    except Exception as e:
        return {"message": "Food not created", "error": str(e)}


async def update_food(
    food_type: str,
    food_data: Annotated[UpdateFood, Body()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        if current_user.user_type.value != UserType.VENDOR.value:
            raise HTTPException(
                status_code=403, detail="Only vendors can update food items"
            )

        # Check if the food exists
        food = await Food.find_one(
            {
                "food_type": food_type,
                "vendor.$id": current_user.id,
            }
        )
        if not food:
            raise HTTPException(status_code=404, detail="Food item not found")

        if food_data.food_name:
            existing_food = await Food.find_one(
                {
                    "food_type": food_data.food_name,
                    "vendor.$id": current_user.id,
                }
            )
            if existing_food:
                raise HTTPException(status_code=400, detail="Food item already exists")

            food.food_type = food_data.food_name
        if food_data.count is not None:
            food.count = food_data.count

        await food.save()
        return {"message": "Food updated"}
    except Exception as e:
        return {"message": "Food not updated", "error": str(e)}


async def delete_food(
    food_type: str,
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type.value != UserType.VENDOR.value:
        raise HTTPException(
            status_code=403, detail="Only vendors can delete food items"
        )

    # Check if the food exists
    food = await Food.find_one({"food_type": food_type, "vendor.$id": current_user.id})
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")

    try:
        await food.delete()
        return {"message": "Food deleted"}
    except Exception as e:
        return {"message": "Food not deleted", "error": str(e)}


async def get_foods_by_vendor(vendor_id: str):
    vendor = await User.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    if vendor.user_type.value != UserType.VENDOR.value:
        raise HTTPException(status_code=403, detail="The given user is not a vendor")

    foods = await Food.find(
        Food.vendor.id == vendor.id,
        sort=[("count", -1)],
    ).to_list()

    return [
        {
            "food_type": food.food_type,
            "count": food.count,
        }
        for food in foods
    ]


async def create_food_collection_request(
    food_type: str, vendor_id: str, current_user: User = Depends(get_current_user)
):
    if current_user.user_type.value != UserType.DEFAULT.value:
        raise HTTPException(
            status_code=403, detail="Only default users can collect food items"
        )

    vendor = await User.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    if vendor.user_type.value != UserType.VENDOR.value:
        raise HTTPException(status_code=403, detail="The given user is not a vendor")
    # Find the food item
    food = await Food.find_one({"food_type": food_type, "vendor.$id": vendor.id})
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")

    # Generate a 6-digit numeric collection code
    collection_code = random.randint(100000, 999999)
    expiration_time = datetime.now() + timedelta(
        minutes=10
    )  # Set expiration time to 10 minutes from now

    # Store the collection code and its expiration time in the food item
    food.collection_codes.append(
        CollectionCode(
            user_id=current_user.id, code=collection_code, expiration=expiration_time
        )
    )

    try:
        await food.save()
        return {
            "message": "Collection code generated",
            "collection_code": collection_code,
        }
    except Exception as e:
        return {"message": "Collection code not generated", "error": str(e)}


async def validate_collection_code(
    food_type: str, collection_code: int, current_user: User = Depends(get_current_user)
):
    if current_user.user_type.value != UserType.VENDOR.value:
        raise HTTPException(
            status_code=403, detail="Only vendors can validate collection codes"
        )

    # Find the food item
    food = await Food.find_one({"food_type": food_type, "vendor.$id": current_user.id})
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")

    # Validate the collection code
    valid_code = None
    for code in food.collection_codes:
        if code.code == collection_code:
            valid_code = code
            break

    if not valid_code:
        raise HTTPException(status_code=400, detail="Invalid collection code")
    if datetime.now() > valid_code.expiration:
        food.collection_codes.remove(valid_code)
        await food.save()
        raise HTTPException(status_code=400, detail="Collection code has expired")

    # Decrease the food count
    if food.count == 0:
        raise HTTPException(status_code=400, detail="Food count is already 0")

    food.count -= 1
    food.collection_codes.remove(valid_code)

    try:
        await food.save()
        return {"message": "Food collected successfully"}
    except Exception as e:
        return {"message": "Food not collected", "error": str(e)}
