import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from models.user_model.user_model import User, CreateUser, UserType, UpdateUser, Status
from models.auth_model.auth_model import TokenData
from models.food_model.food_model import Food

from fastapi import Depends, HTTPException, status, Form, Body
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from config.config import Settings

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime

from bson.objectid import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def send_verification_email(to_address: str):
    # Generate a 6-digit numeric verification code
    verification_code = random.randint(100000, 999999)
    expiration_time = datetime.now() + timedelta(
        minutes=10
    )  # Set expiration time to 10 minutes from now

    # TODO: Move these to environment variables
    mailUsername = Settings().MAIL_USERNAME
    mailPassword = Settings().MAIL_PASSWORD

    # print("Sending email to: ", to_address)
    from_addr = Settings().MAIL_USERNAME

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_address
    msg["Subject"] = "Verification Code"
    body = f"Your verification code is: {verification_code}"
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(mailUsername, mailPassword)
        server.sendmail(from_addr, to_address, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send verification email: {str(e)}"
        )

    # Store the verification code and its expiration time in the user's record
    try:
        user = await get_user_from_db(to_address)
        user.verification_code = verification_code
        user.verification_code_expiration = expiration_time
        await user.save()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save verification code: {str(e)}"
        )

    return {"message": "Verification email sent"}


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
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed_password = get_password_hash(form_data.password)
    try:
        await User.insert_one(
            User(
                **form_data.model_dump(),
                hashed_password=hashed_password,
            )
        )
        newUser = await get_user_from_db(form_data.email)
        newUser.disabled = True
        await newUser.save()
        await send_verification_email(newUser.email)
        return {"message": "User created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User not created: {str(e)}")


async def list_vendors():
    vendors = await User.find(User.user_type == UserType.VENDOR.value).to_list()

    vendor_list = []
    for vendor in vendors:
        total_count = await Food.find(Food.vendor.id == vendor.id).sum("count")
        if total_count is None:
            total_count = 0  # Set default value if total_count is None
        vendor_list.append(
            {
                "vendor": vendor,
                "total_count": total_count,
            }
        )

    vendor_list.sort(
        key=lambda x: x["total_count"],
        reverse=True,
    )

    vendor_list.sort(
        key=lambda x: x["vendor"].status,
        reverse=True,
    )

    return vendor_list


async def get_user_by_id(user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        return user
    except Exception as e:
        return {"message": "User not found", "error": str(e)}


async def update_user(
    user_data: Annotated[UpdateUser, Body()],
    current_user: User = Depends(get_current_user),
):
    try:
        update_data = user_data.model_dump(
            exclude_unset=True,
        )

        # Convert empty strings to None
        for key, value in update_data.items():
            if value == "" or (
                key == "status" and current_user.user_type == UserType.DEFAULT
            ):
                update_data[key] = None

        # if "current_password" in update_data and "new_password" in update_data:
        # if update_data["current_password"] and update_data["new_password"]:
        if "current_password" in update_data and "new_password" in update_data:
            if not verify_password(
                update_data["current_password"],
                current_user.hashed_password,
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Incorrect current password",
                )
            update_data["hashed_password"] = get_password_hash(
                update_data["new_password"]
            )
            del update_data["current_password"]
            del update_data["new_password"]

        for key, value in update_data.items():
            if value is not None:
                setattr(current_user, key, value)

        current_user.updated_at = datetime.now()

        await current_user.save()

        return {"message": "User updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User not updated: {str(e)}")


async def delete_user(current_user: User = Depends(get_current_user)):
    try:
        await current_user.delete()
        return {"message": "User deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User not deleted: {str(e)}")
