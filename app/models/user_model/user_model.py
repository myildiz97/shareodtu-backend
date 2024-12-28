from enum import Enum
from beanie import Document
from datetime import datetime, timedelta
from pydantic import Field, EmailStr, BaseModel
from fastapi import Form

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
    forgot_password_code: Optional[int] = Field(None, example=123456)
    forgot_password_code_expiration: Optional[datetime] = Field(None, example=datetime.now())


class CreateUser(BaseModel):
    full_name: str = Form(..., example="John Doe")
    email: EmailStr = Form(..., example="johndoe@example.com")
    password: str = Form(..., example="password")
    user_type: UserType = Form(UserType.DEFAULT.value, example=UserType.DEFAULT.value)
    status: Status = Form(Status.OPEN, example=Status.OPEN)


class UpdateUser(BaseModel):
    full_name: Optional[str] = Field(None, example="John Doe")
    current_password: Optional[str] = Field(None, example="password")
    new_password: Optional[str] = Field(None, example="password")
    status: Optional[Status] = Field(None, example=Status.OPEN)
