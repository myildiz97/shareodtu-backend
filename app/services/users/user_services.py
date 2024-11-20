from models.user_model.user_model import User, CreateUser, UserType
from models.auth_model.auth_model import TokenData

from fastapi import Depends, HTTPException, status, Form
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from config.config import Settings

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_from_db(email: str) -> User | None:
    try:
        user = await User.find_one(User.email == email)
        return user
    except Exception as e:
        return {"message": "User not found", "error": str(e)}


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, Settings().SECRET_KEY, algorithms=[Settings().ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_from_db(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def create_user(form_data: Annotated[CreateUser, Form()]):
    existing_user = await get_user_from_db(form_data.email)
    print("existing_user", existing_user)
    if existing_user:
        print("User already exists")
        raise HTTPException(status_code=409, detail="User already exists")

    print("Creating user")
    hashed_password = get_password_hash(form_data.password)
    try:
        await User.insert_one(
            User(
                **form_data.model_dump(),
                hashed_password=hashed_password,
            )
        )
        return {"message": "User created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User not created: {str(e)}")


async def list_vendors():
    vendors = await User.find(User.user_type == UserType.VENDOR.value).to_list()

    # Also return total food count for each vendor
    return [vendor.full_name for vendor in vendors]


# async def list_foods_by_vendor():
