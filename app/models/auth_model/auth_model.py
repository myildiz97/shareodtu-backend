from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
    token_type: str = Field(..., example="bearer")


class TokenData(BaseModel):
    email: EmailStr | None = None


class VerificationData(BaseModel):
    email: EmailStr | None = None
    code: int = Field(..., example=123456)
