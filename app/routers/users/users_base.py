from typing import Annotated
from models.user_model.user_model import User, CreateUser, UpdateUser, RegisterVendor
from services.users.user_services import (
    get_current_active_user,
    create_user as create_user_service,
    list_vendors as list_vendors_service,
    get_user_by_id,
    update_user as update_user_service,
    delete_user as delete_user_service,
    register_vendor as register_vendor_service,
    list_waiting_vendors as list_waiting_vendors_service,
    approve_vendor as approve_vendor_service,
    get_user_type_by_email as get_user_type_by_email_service,
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

@router.get("/type/{email}")
async def get_user_type_by_email(email: str):
    return await get_user_type_by_email_service(email)


@router.post("/create")
async def create_user(form_data: Annotated[CreateUser, Form()]):
    return await create_user_service(form_data)


@router.post("/register_vendor")
async def register_vendor(form_data: Annotated[RegisterVendor, Form()]):
    return await register_vendor_service(form_data)

@router.put("/approve_vendor/{user_id}")
async def approve_vendor(user_id: str):
    return await approve_vendor_service(user_id)

@router.get("/vendors")
async def list_vendors():
    return await list_vendors_service()

@router.get("/approval_waiting_vendors")
async def list_waiting_vendors():
    return await list_waiting_vendors_service()

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
