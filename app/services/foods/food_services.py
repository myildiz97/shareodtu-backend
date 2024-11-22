from models.food_model.food_model import Food
from services.users.user_services import get_current_user
from fastapi import Depends, HTTPException
from models.user_model.user_model import UserType, User


async def create_food(food_type: str, current_user: User = Depends(get_current_user)):
    if current_user.user_type.value != UserType.VENDOR.value:
        raise HTTPException(
            status_code=403, detail="Only vendors can create food items"
        )

    # Check if the food already exists
    existing_food = await Food.find_one(
        {"food_type": food_type, "vendor.$id": current_user.id}
    )
    if existing_food:
        raise HTTPException(status_code=400, detail="Food item already exists")

    food = Food(food_type=food_type, vendor=current_user)

    try:
        await food.insert()
        return {"message": "Food created"}
    except Exception as e:
        return {"message": "Food not created", "error": str(e)}


async def increase_food_count(
    food_type: str, current_user: User = Depends(get_current_user)
):
    if current_user.user_type.value != UserType.VENDOR.value:
        raise HTTPException(
            status_code=403, detail="Only vendors can increase food count"
        )

    # Find the food item
    food = await Food.find_one({"food_type": food_type, "vendor.$id": current_user.id})
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found")

    # Increase the food count
    food.count += 1

    try:
        await food.save()
        return {"message": "Food count increased"}
    except Exception as e:
        return {"message": "Food count not increased", "error": str(e)}


async def get_foods_by_vendor(vendor_id: str):
    vendor = await User.get(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    if vendor.user_type.value != UserType.VENDOR.value:
        raise HTTPException(status_code=403, detail="The given user is not a vendor")

    foods = await Food.find(Food.vendor.id == vendor.id).to_list()

    return [
        {
            "food_type": food.food_type,
            "count": food.count,
        }
        for food in foods
    ]
