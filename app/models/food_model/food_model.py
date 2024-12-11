from datetime import datetime, timedelta
from beanie import Document, Link
from pydantic import Field, BaseModel
from models.user_model.user_model import User
from fastapi import Form, Body
from typing import List, Optional, Dict


class CollectionCode(BaseModel):
    code: int
    expiration: datetime


class Food(Document):
    food_type: str = Field(..., example="Pizza")
    count: int = Field(0, example=10)
    vendor: Link[User] = Field(..., example="User")
    collection_codes: List[Optional[CollectionCode]] = Field(default_factory=list)


class CreateFood(BaseModel):
    food_type: str = Form(..., example="Pizza")
    count: int = Form(..., example=10)


class UpdateFood(BaseModel):
    food_name: Optional[str] = Body(None, example="Pizza")
    count: Optional[int] = Body(None, example=10)
