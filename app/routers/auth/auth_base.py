from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from services.auth.auth_services import (
    authenticate_user,
    create_access_token,
    verify_user,
    send_verification_email as send_verification_email_service,
    send_forgot_password_email as send_forgot_password_email_service,
)
from config.config import Settings
from datetime import timedelta

from models.auth_model.auth_model import Token, VerificationData

from fastapi import APIRouter, Depends, Body

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


@router.post("/verify")
async def verify(
    verification_data: Annotated[VerificationData, Body()],
):
    return await verify_user(
        verification_data,
    )


@router.post("/send_verification_email/{email}")
async def send_verification_email(email: str):
    return await send_verification_email_service(email)

@router.post("/send_forgot_password_email/{email}")
async def send_forgot_password_email(email: str):
    return await send_forgot_password_email_service(email)
