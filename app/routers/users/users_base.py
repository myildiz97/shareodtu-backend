from typing import Annotated
from models.user_model.user_model import User, CreateUser
from services.users.user_services import (
    get_current_active_user,
    create_user as create_user_service,
)

from fastapi import (
    APIRouter,
    Depends,
    Form,
)

router = APIRouter(
    prefix="/users",
    tags=["Users Base"],
)


@router.get("/me")
async def get_user_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.post("/create")
async def create_user(form_data: Annotated[CreateUser, Form()]):
    return await create_user_service(form_data)
