from models.user_model.user_model import User
from services.users.user_services import get_user_from_db, verify_password
from config.config import Settings

from datetime import datetime, timedelta, timezone

import jwt

from fastapi import HTTPException, status


async def authenticate_user(email: str, password: str) -> User:
    user = await get_user_from_db(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Inactive user, please verify your email",
        )
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        Settings().SECRET_KEY,
        algorithm=Settings().ALGORITHM,
    )
    return encoded_jwt
