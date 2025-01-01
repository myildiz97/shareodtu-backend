from enum import Enum
from beanie import Document
from datetime import datetime, timedelta
from pydantic import Field, EmailStr, BaseModel
from fastapi import Form, UploadFile, HTTPException

from typing import Optional


class UserType(str, Enum):
    DEFAULT = "default"
    ADMIN = "admin"
    VENDOR = "vendor"


class Status(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"


class User(Document):
    full_name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="johndoe@example.com")
    hashed_password: str = Field(
        ..., example="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    disabled: bool = Field(False, example=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user_type: UserType = Field(UserType.DEFAULT.value, example=UserType.DEFAULT.value)
    status: Status = Field(Status.OPEN, example=Status.OPEN)
    verification_code: Optional[int] = Field(None, example=123456)
    verification_code_expiration: Optional[datetime] = Field(None, example=datetime.now())
    reset_password_code: Optional[int] = Field(None, example=123456)
    reset_password_code_expiration: Optional[datetime] = Field(None, example=datetime.now())
    
    # vendor registration request
    vendor_address: Optional[str] = Field(None, example="Informatics Institute Building, 7th Floor, Room 705")
    facility_name: Optional[str] = Field(None, example="Kumpir Cafe")
    vendor_phone: Optional[str] = Field(None, example="03122223344")
    vendor_identity_no: Optional[str] = Field(None, example="12345678910")
    image: Optional[bytes] = None
    # vendor_id_photo:

class CreateUser(BaseModel):
    full_name: str = Form(..., example="John Doe")
    email: EmailStr = Form(..., example="johndoe@example.com")
    password: str = Form(..., example="password")
    user_type: UserType = Form(UserType.DEFAULT.value, example=UserType.DEFAULT.value)

class UpdateUser(BaseModel):
    full_name: Optional[str] = Field(None, example="John Doe")
    current_password: Optional[str] = Field(None, example="password")
    new_password: Optional[str] = Field(None, example="password")
    status: Optional[Status] = Field(None, example=Status.OPEN)

class RegisterVendor(BaseModel):
    full_name: str = Form(..., example="John Doe")
    email: EmailStr = Form(..., example="johndoe@example.com")
    password: str = Form(..., example="password")
    user_type: UserType = Form(UserType.VENDOR.value, example=UserType.VENDOR.value)
    vendor_address: Optional[str] = Field(None, example="Informatics Institute Building, 7th Floor, Room 705")
    facility_name: Optional[str] = Field(None, example="Kumpir Cafe")
    vendor_phone: Optional[str] = Field(None, example="03122223344")
    vendor_identity_no: Optional[str] = Field(None, example="12345678910")
    image: Optional[bytes] = None  # Field to store the image as binary data