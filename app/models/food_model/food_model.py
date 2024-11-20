from beanie import Document, Link
from pydantic import Field, BaseModel
from models.user_model.user_model import User
from fastapi import Form


class Food(Document):
    food_type: str = Field(..., example="Pizza")
    count: int = Field(0, example=10)
    vendor: Link[User] = Field(..., example="User")


class CreateFood(BaseModel):
    food_type: str = Form(..., example="Pizza")
    count: int = Form(..., example=10)
