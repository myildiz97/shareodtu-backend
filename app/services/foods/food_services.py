from models.user_model.user_model import User, CreateUser, UserType
from models.food_model.food_model import Food, CreateFood
from services.users.user_services import get_current_user

from fastapi import Depends, HTTPException, status, Form
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from config.config import Settings

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext


async def create_food(food_type: str):
    current_user = get_current_user()
    if current_user.user_type != UserType.VENDOR.value:
        raise HTTPException(
            status_code=403, detail="Only vendors can create food items"
        )

    food = Food(food_type=food_type, count=0, vendor_name=current_user.full_name)

    try:
        await Food.insert_one(
            food
        )
        return {"message": "Food created"}
    except Exception as e:
        return {"message": "Food not created", "error": str(e)}
    

# async def increase_food_count(food_type: str):
#     current_user = get_current_user()
#     if current_user.user_type != UserType.VENDOR.value:
#         raise HTTPException(
#             status_code=403, detail="Only vendors can create food items"
#         )
#     food = await Food.find_one(Food.id == food_id)
#     if not food:
#         raise HTTPException(
#             status_code=404, detail="Food not found"
#         )

#     food.count += 1

#     try:
#         await Food.update_one(
#             Food.id == food_id,
#             food
#         )
#         return {"message": "Food count increased"}
#     except Exception as e:
#         return {"message": "Food count not increased", "error": str(e)}
