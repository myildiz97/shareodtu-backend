from typing import Annotated
from models.user_model.user_model import User, CreateUser, UpdateUser
from services.users.user_services import (
    get_current_active_user,
    create_user as create_user_service,
    list_vendors as list_vendors_service,
    get_user_by_id,
    update_user as update_user_service,
    delete_user as delete_user_service,
    send_verification_email as send_verification_email_service,
    verify_code as verify_code_service,
)

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Body,
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


@router.get("/vendors")
async def list_vendors():
    return await list_vendors_service()


@router.get("/{user_id}")
async def get_user_id(user_id: str):
    return await get_user_by_id(user_id)


@router.put("/me")
async def update_user(
    user_data: Annotated[UpdateUser, Body()],
    current_user: User = Depends(get_current_active_user),
):
    return await update_user_service(user_data, current_user)


@router.delete("/me")
async def delete_user(current_user: User = Depends(get_current_active_user)):
    return await delete_user_service(current_user)

@router.post("/send_verification_email")
async def send_verification_email(to_address: str):
    return await send_verification_email_service(to_address)

@router.post("/verify_code")
async def verify_code(to_address: str, code: int):
    return await verify_code_service(to_address, code)
