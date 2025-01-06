from typing import Annotated, Optional
from pydantic import EmailStr
from models.user_model.user_model import (
    User,
    CreateUser,
    UpdateUser,
    RegisterVendor,
    UserType,
    UpdateUserByAdmin,
    UpdateVendorByAdmin,
    RegisterVendorByAdmin,
)
from services.users.user_services import (
    get_current_active_user,
    create_user as create_user_service,
    list_vendors as list_vendors_service,
    get_user_by_id,
    update_user as update_user_service,
    delete_user as delete_user_service,
    register_vendor as register_vendor_service,
    approve_vendor as approve_vendor_service,
    reject_vendor as reject_vendor_service,
    get_user_type_by_email as get_user_type_by_email_service,
    get_image_content,
    delete_user_as_admin as delete_user_as_admin_service,
    update_user_as_admin as update_user_as_admin_service,
    update_vendor_as_admin as update_vendor_as_admin_service,
    create_user_by_admin as create_user_by_admin_service,
    create_vendor_by_admin as create_vendor_by_admin_service,
)
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
from io import BytesIO

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


@router.get("/")
async def list_users():
    return await User.find().sort([("updated_at", -1)]).to_list()


@router.post("/create/user")
async def create_user_as_admin(
    user_data: Annotated[CreateUser, Body()],
    current_user: User = Depends(get_current_active_user),
):
    return await create_user_by_admin_service(
        user_data,
        current_user,
    )


@router.post("/create/vendor")
async def create_vendor_as_admin(
    vendor_data: Annotated[RegisterVendorByAdmin, Body()],
    current_user: User = Depends(get_current_active_user),
):
    return await create_vendor_by_admin_service(
        vendor_data,
        current_user,
    )


@router.put("/user/{user_id}")
async def update_user_as_admin(
    user_id: str,
    user_data: Annotated[UpdateUserByAdmin, Body()],
    current_user: User = Depends(get_current_active_user),
):
    return await update_user_as_admin_service(
        user_id,
        user_data,
        current_user,
    )


@router.put("/vendor/{user_id}")
async def update_vendor_as_admin(
    user_id: str,
    vendor_data: Annotated[UpdateVendorByAdmin, Body()],
    current_user: User = Depends(get_current_active_user),
):
    return await update_vendor_as_admin_service(
        user_id,
        vendor_data,
        current_user,
    )


@router.delete("/{user_id}")
async def delete_user_as_admin(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
):
    return await delete_user_as_admin_service(
        user_id,
        current_user,
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
async def create_user(
    form_data: Annotated[CreateUser, Form()],
):
    return await create_user_service(form_data)


@router.post("/register_vendor")
async def register_vendor(
    full_name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    vendor_address: str = Form(...),
    facility_name: str = Form(...),
    vendor_phone: str = Form(...),
    vendor_identity_no: str = Form(...),
    image: UploadFile = File(..., media_type="image/jpeg"),
):
    image_data = await get_image_content(image)
    form_data_dict = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "user_type": UserType.VENDOR.value,
        "vendor_address": vendor_address,
        "facility_name": facility_name,
        "vendor_phone": vendor_phone,
        "vendor_identity_no": vendor_identity_no,
        "image": image_data,
    }

    form_data = RegisterVendor(
        **form_data_dict,
    )

    return await register_vendor_service(form_data)


@router.get("/approve_vendor/{user_id}")
async def approve_vendor(user_id: str):
    return await approve_vendor_service(user_id)


@router.get("/reject_vendor/{user_id}")
async def reject_vendor(user_id: str):
    return await reject_vendor_service(user_id)


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


@router.get("/{user_id}/image")
async def get_user_image(
    user_id: str, current_user: User = Depends(get_current_active_user)
):
    if current_user.user_type != UserType.ADMIN.value:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this resource",
        )
    user = await User.find_one(User.id == ObjectId(user_id))
    if not user or not user.image:
        raise HTTPException(
            status_code=404,
            detail="User or image not found",
        )

    image_stream = BytesIO(user.image)
    return StreamingResponse(
        image_stream,
        media_type="image/jpeg",
    )
