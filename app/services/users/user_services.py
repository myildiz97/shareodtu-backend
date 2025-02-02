from models.user_model.user_model import (
    User,
    CreateUser,
    UserType,
    UpdateUser,
    RegisterVendor,
    UpdateUserByAdmin,
    UpdateVendorByAdmin,
    RegisterVendorByAdmin,
)
from models.auth_model.auth_model import TokenData, ResetPasswordData
from models.food_model.food_model import Food
from services.auth.auth_services import (
    send_verification_email,
    send_approval_waiting_email,
    send_approval_email,
    send_rejection_email,
)
from services.shared.shared_services import get_user_from_db, verify_password

from fastapi import Depends, HTTPException, status, Form, Body, UploadFile
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from config.config import Settings

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from bson.objectid import ObjectId
import base64


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, Settings().SECRET_KEY, algorithms=[Settings().ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_from_db(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_user_type_by_email(email: str):
    user = await get_user_from_db(email)
    if user:
        return user.user_type
    raise HTTPException(status_code=404, detail="User not found")


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def create_user(form_data: Annotated[CreateUser, Form()]):
    existing_user = await get_user_from_db(form_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed_password = get_password_hash(form_data.password)
    try:
        await User.insert_one(
            User(
                **form_data.model_dump(),
                hashed_password=hashed_password,
            )
        )
        newUser = await get_user_from_db(form_data.email)
        newUser.disabled = True
        await newUser.save()
        await send_verification_email(newUser.email)
        return {"message": "User created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User not created: {str(e)}")


async def list_vendors():
    vendors = await User.find(User.user_type == UserType.VENDOR.value).to_list()

    vendor_list = []
    for vendor in vendors:
        total_count = await Food.find(Food.vendor.id == vendor.id).sum("count")
        if total_count is None:
            total_count = 0  # Set default value if total_count is None
        vendor_list.append(
            {
                "vendor": vendor,
                "total_count": total_count,
            }
        )

    vendor_list.sort(
        key=lambda x: x["total_count"],
        reverse=True,
    )

    vendor_list.sort(
        key=lambda x: x["vendor"].status,
        reverse=True,
    )

    return vendor_list


async def get_user_by_id(user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        return user
    except Exception as e:
        return {"message": "User not found", "error": str(e)}


async def update_user(
    user_data: Annotated[UpdateUser, Body()],
    current_user: User = Depends(get_current_user),
):
    try:
        update_data = user_data.model_dump(
            exclude_unset=True,
        )

        # Convert empty strings to None
        for key, value in update_data.items():
            if value == "" or (
                key == "status" and current_user.user_type == UserType.DEFAULT
            ):
                update_data[key] = None

        # if "current_password" in update_data and "new_password" in update_data:
        # if update_data["current_password"] and update_data["new_password"]:
        if "current_password" in update_data and "new_password" in update_data:
            if not verify_password(
                update_data["current_password"],
                current_user.hashed_password,
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Incorrect current password",
                )
            update_data["hashed_password"] = get_password_hash(
                update_data["new_password"]
            )
            del update_data["current_password"]
            del update_data["new_password"]

        for key, value in update_data.items():
            if value is not None:
                setattr(current_user, key, value)

        current_user.updated_at = datetime.now()

        await current_user.save()

        return {"message": "User updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User not updated: {str(e)}")


async def delete_user(current_user: User = Depends(get_current_user)):
    try:
        await current_user.delete()
        return {"message": "User deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User not deleted: {str(e)}")


async def register_vendor(
    form_data: Annotated[RegisterVendor, Form()],
):
    existing_user = await get_user_from_db(form_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed_password = get_password_hash(form_data.password)
    try:
        await User.insert_one(
            User(
                **form_data.model_dump(),
                hashed_password=hashed_password,
            )
        )
        newUser = await get_user_from_db(form_data.email)
        newUser.disabled = True
        await newUser.save()
        await send_approval_waiting_email(newUser.email)
        return {"message": "User created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User not created: {str(e)}")


async def approve_vendor(user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        user.disabled = False
        await user.save()
        await send_approval_email(user.email)
        return {"message": "Vendor approved"}
    except Exception as e:
        return {"message": "Vendor could not approved", "error": str(e)}


async def reject_vendor(user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        await user.delete()
        await send_rejection_email(user.email)
        return {"message": "Vendor rejected"}
    except Exception as e:
        return {"message": "Vendor could not rejected", "error": str(e)}


async def get_image_content(file: UploadFile) -> bytes:
    try:
        contents = await file.read()
        encoded_content = base64.b64encode(contents).decode("utf-8")
        return encoded_content
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get image content: {str(e)}",
        )


async def reset_user_password(
    data: Annotated[ResetPasswordData, Body()],
):
    user = await get_user_from_db(data.email)
    if user:
        if data.reset_token != user.reset_token:
            raise HTTPException(
                status_code=400,
                detail="Invalid reset token",
            )
        if user.reset_token_expiration < datetime.now():
            raise HTTPException(
                status_code=400,
                detail="Reset token expired! Please request a new one",
            )

        hashed_password = get_password_hash(data.password)
        user.hashed_password = hashed_password
        user.reset_token = None
        user.reset_token_expiration = None
        await user.save()
        return {"message": "Password reset successfully"}
    raise HTTPException(
        status_code=404,
        detail="User not found",
    )


async def delete_user_as_admin(
    user_id: str,
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this resource",
        )

    try:
        user = await User.find_one(
            User.id == ObjectId(user_id),
        )
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        if user.user_type == UserType.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to delete this user",
            )
        if user.user_type == UserType.VENDOR:
            foods = await Food.find(Food.vendor.id == user.id).to_list()
            for food in foods:
                await food.delete()
        await user.delete()
        return {"message": "User deleted"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"User not deleted: {str(e)}",
        )


async def update_user_as_admin(
    user_id: str,
    user_data: Annotated[UpdateUserByAdmin, Body()],
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this resource",
        )

    try:
        user = await User.find_one(
            User.id == ObjectId(user_id),
        )
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        update_data = user_data.model_dump(
            exclude_unset=True,
        )

        # Convert empty strings to None
        for key, value in update_data.items():
            if value == "":
                update_data[key] = None

        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)

        user.updated_at = datetime.now()

        await user.save()

        return {"message": "User updated"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"User not updated: {str(e)}",
        )


async def update_vendor_as_admin(
    user_id: str,
    vendor_data: Annotated[UpdateVendorByAdmin, Body()],
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this resource",
        )

    try:
        user = await User.find_one(
            User.id == ObjectId(user_id),
        )
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )

        update_data = vendor_data.model_dump(
            exclude_unset=True,
        )

        # Convert empty strings to None
        for key, value in update_data.items():
            if value == "":
                update_data[key] = None

        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)

        user.updated_at = datetime.now()

        await user.save()

        return {"message": "Vendor updated"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vendor not updated: {str(e)}",
        )


async def create_user_by_admin(
    form_data: Annotated[CreateUser, Form()],
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this resource",
        )

    existing_user = await get_user_from_db(form_data.email)
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User already exists",
        )

    hashed_password = get_password_hash(form_data.password)
    try:
        await User.insert_one(
            User(
                **form_data.model_dump(),
                hashed_password=hashed_password,
            )
        )
        return {"message": "User created"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"User not created: {str(e)}",
        )


async def create_vendor_by_admin(
    form_data: Annotated[RegisterVendorByAdmin, Form()],
    current_user: User = Depends(get_current_user),
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this resource",
        )

    existing_user = await get_user_from_db(form_data.email)
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User already exists",
        )

    hashed_password = get_password_hash(form_data.password)
    try:
        await User.insert_one(
            User(
                **form_data.model_dump(),
                hashed_password=hashed_password,
            )
        )
        return {"message": "User created"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"User not created: {str(e)}",
        )
