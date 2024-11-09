from beanie import Document
from datetime import datetime
from pydantic import Field, EmailStr, BaseModel


class User(Document):
    username: str = Field(..., example="johndoe")
    email: EmailStr = Field(..., example="johndoe@example.com")
    hashed_password: str = Field(
        ..., example="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    disabled: bool = Field(False, example=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreateUser(BaseModel):
    username: str = Field(..., example="johndoe")
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(..., example="password")
