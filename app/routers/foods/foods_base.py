from typing import Annotated
from models.user_model.user_model import User

from services.foods.food_services import (
    create_food as create_food_service,
    delete_food as delete_food_service,
    increase_food_count as increase_food_count_service,
    decrease_food_count as decrease_food_count_service,
    update_food_count as update_food_count_service,
    get_food_count as get_food_count_service,
    get_foods_by_vendor as get_foods_by_vendor_service,
)

from services.users.user_services import get_current_user
from fastapi import Depends, APIRouter, Form

router = APIRouter(
    prefix="/foods",
    tags=["Foods Base"],
)


@router.post("/create")
async def create_food(food_type: str, current_user: User = Depends(get_current_user)):
    return await create_food_service(food_type, current_user)


@router.post("/increase_count")
async def increase_food_count(food_type: str, current_user: User = Depends(get_current_user)):
    return await increase_food_count_service(food_type, current_user)


@router.post("/decrease_count")
async def decrease_food_count(food_type: str, current_user: User = Depends(get_current_user)):
    return await decrease_food_count_service(food_type, current_user)


@router.get("/list/{vendor_id}")
async def get_foods_by_vendor(vendor_id: str):
    return await get_foods_by_vendor_service(vendor_id)

@router.delete("/delete")
async def delete_food(food_type: str, current_user: User = Depends(get_current_user)):
    return await delete_food_service(food_type, current_user)


@router.put("/update_count")
async def update_food_count(food_type: str, count: int, current_user: User = Depends(get_current_user)):
    return await update_food_count_service(food_type, count, current_user)


@router.get("/get_count")
async def get_food_count(food_type: str, vendor_id: str):
    return await get_food_count_service(food_type, vendor_id)
