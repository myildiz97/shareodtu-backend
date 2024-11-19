from enum import Enum
from beanie import Document
from datetime import datetime
from pydantic import Field, EmailStr, BaseModel
from fastapi import Form

class UserType(Enum):
    DEFAULT = "default"
    ADMIN = "admin"
    VENDOR = "vendor"

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

class CreateUser(BaseModel):
    full_name: str = Form(..., example="John Doe")
    email: EmailStr = Form(..., example="johndoe@example.com")
    password: str = Form(..., example="password")
    user_type: UserType = Form(..., example=UserType.DEFAULT.value)
