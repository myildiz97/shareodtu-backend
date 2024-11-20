from beanie import Document
from pydantic import Field, BaseModel
from fastapi import Form


class Food(Document):
    food_type: str = Field(..., example="Pizza")
    count: int = Field(0, example=10)
    vendor_name: str = Field(..., example="John Doe")
    # TODO: link the user instead of the vendor name
    # vendor: User = Field(..., example=User)


class CreateFood(BaseModel):
    food_type: str = Form(..., example="Pizza")
    count: int = Form(..., example=10)
    vendor_name: str = Form(..., example="John Doe")
