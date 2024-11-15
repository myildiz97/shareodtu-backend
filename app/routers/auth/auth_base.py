from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from services.auth.auth_services import authenticate_user, create_access_token
from config.config import Settings
from datetime import timedelta

from models.auth_model.auth_model import Token

from fastapi import APIRouter, Depends

from datetime import timedelta

router = APIRouter(
    tags=["Auth Base"],
)


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=Settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
