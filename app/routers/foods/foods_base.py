from typing import Annotated
from models.user_model.user_model import User
from models.food_model.food_model import Food, CreateFood
from services.foods.food_services import create_food as create_food_service
from services.users.user_services import get_current_user  # Import get_current_user
from fastapi import Depends, APIRouter, Form

router = APIRouter(
    prefix="/foods",
    tags=["Foods Base"],
)

@router.post("/create")
async def create_food(food_type: str, current_user: User = Depends(get_current_user)):
    return await create_food_service(food_type, current_user)

