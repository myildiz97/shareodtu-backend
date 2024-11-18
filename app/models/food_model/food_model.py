from beanie import Document
from pydantic import Field, BaseModel
from fastapi import Form

class Food(Document):
    food_type: str = Field(..., example="Fruit")
    count: int = Field(0, example=10)
    vendor_name: str = Field(..., example="John Doe")
   


class CreateFood(BaseModel):
    food_type: str = Form(..., example="Fruit")
    count: int = Form(..., example=10)
    vendor_name: str = Form(..., example="John Doe")