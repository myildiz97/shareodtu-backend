from typing import Annotated, Optional
from models.user_model.user_model import User
from models.food_model.food_model import (
    UpdateFood,
    CreateFood,
    CollectFoodData,
    ValidateCollectionCode,
)

from services.foods.food_services import (
    create_food as create_food_service,
    delete_food as delete_food_service,
    get_foods_by_vendor as get_foods_by_vendor_service,
    create_food_collection_request as create_food_collection_request_service,
    validate_collection_code as validate_collection_code_service,
    update_food as update_food_service,
    create_food_admin as create_food_admin_service,
    update_food_admin as update_food_admin_service,
    delete_food_admin as delete_food_admin_service,
)

from services.users.user_services import get_current_user
from fastapi import Depends, APIRouter, Body

router = APIRouter(
    prefix="/foods",
    tags=["Foods Base"],
)


@router.post("/create")
async def create_food(
    food_data: Annotated[CreateFood, Body()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_food_service(
        food_data=food_data,
        current_user=current_user,
    )


@router.put("/update/{food_type}")
async def update_food(
    food_type: str,
    food_data: Annotated[UpdateFood, Body()],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await update_food_service(
        food_data=food_data,
        food_type=food_type,
        current_user=current_user,
    )


@router.get("/list/{vendor_id}")
async def get_foods_by_vendor(vendor_id: str):
    return await get_foods_by_vendor_service(vendor_id)


@router.delete("/delete/{food_type}")
async def delete_food(
    food_type: str,
    current_user: User = Depends(get_current_user),
):
    return await delete_food_service(food_type, current_user)


@router.post("/collect")
async def create_food_collection_request(
    collect_food_data: Annotated[CollectFoodData, Body()],
    current_user: User = Depends(get_current_user),
):
    return await create_food_collection_request_service(
        food_type=collect_food_data.food_type,
        vendor_id=collect_food_data.vendor_id,
        current_user=current_user,
    )


@router.post("/validate_collection_code")
async def validate_collection_code(
    validate_collection_code_data: Annotated[ValidateCollectionCode, Body()],
    current_user: User = Depends(get_current_user),
):
    return await validate_collection_code_service(
        food_type=validate_collection_code_data.food_type,
        collection_code=validate_collection_code_data.collection_code,
        current_user=current_user,
    )

@router.post("/create_food_admin")
async def create_food_admin(
    food_data: Annotated[CreateFood, Body()],
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await create_food_admin_service(
        food_data=food_data,
        vendor_id=vendor_id,
        current_user=current_user,
    )

@router.put("/update_food_admin/{food_type}")
async def update_food_admin(
    food_type: str,
    food_data: Annotated[UpdateFood, Body()],
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await update_food_admin_service(
        food_data=food_data,
        food_type=food_type,
        vendor_id=vendor_id,
        current_user=current_user,
    )

@router.delete("/delete_food_admin/{food_type}")
async def delete_food_admin(
    food_type: str,
    vendor_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    return await delete_food_admin_service(
        food_type=food_type,
        vendor_id=vendor_id,
        current_user=current_user,
    )
