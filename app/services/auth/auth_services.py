from models.user_model.user_model import User
from models.auth_model.auth_model import VerificationData
from services.shared.shared_services import get_user_from_db, verify_password
from config.config import Settings

from datetime import datetime, timedelta, timezone

import jwt

from fastapi import HTTPException, status

import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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


async def verify_user(
    verification_data: VerificationData,
):
    try:
        user = await get_user_from_db(verification_data.email)

        if user.verification_code != verification_data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        if datetime.now() > user.verification_code_expiration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired",
            )

        user.verification_code = None
        user.verification_code_expiration = None
        user.disabled = False

        await user.save()
        return {"message": "User verified"}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        # Log unexpected errors here if needed
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify user",
        )


async def send_code(email: str, message: str):
    # Generate a 6-digit numeric verification code
    verification_code = random.randint(100000, 999999)

    mailUsername = Settings().MAIL_USERNAME
    mailPassword = Settings().MAIL_PASSWORD

    print("Sending email to: ", email)
    from_addr = Settings().MAIL_USERNAME

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = email
    msg["Subject"] = "Verification Code"
    body = f"{message}{verification_code}"
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(mailUsername, mailPassword)
        server.sendmail(from_addr, email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send verification email: {str(e)}"
        )    
    return verification_code

async def send_verification_email(email: str):
    # Set expiration time to 10 minutes from now
    expiration_time = datetime.now() + timedelta(minutes=10)

    verification_code = await send_code(email, "To verify your account, please enter the code: ")

    # Store the verification code and its expiration time in the user's record
    try:
        user = await get_user_from_db(email)
        user.verification_code = verification_code
        user.verification_code_expiration = expiration_time
        await user.save()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save verification code: {str(e)}"
        )

    return {"message": "Verification email sent"}

async def send_reset_password_email(email: str): 
    user = await get_user_from_db(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Inactive user, please verify your email",
        )
    
    # Set expiration time to 10 minutes from now
    expiration_time = datetime.now() + timedelta(minutes=10)
    reset_password_code = await send_code(email, "To reset your password, please enter the code: ")

    # Store the verification code and its expiration time in the user's record
    try:
        user.reset_password_code = reset_password_code
        user.reset_password_code_expiration = expiration_time
        await user.save()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save verification code: {str(e)}"
        )

    return {"message": "Reset password email sent"}
