# -*- coding: utf-8 -*-
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt

from app.config import config
from app.models import User
from app.enums import LoginStatusEnum
from app.security import employee_verify, totp_verify


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_user_token(user: User) -> str:
    """
    Generates a JWT access token for a given user.
    Args:
        user (User): The user object for which the token is being generated.
    Returns:
        str: The generated JWT access token.
    """

    access_token_expires = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return access_token

async def authenticate_user(
    username: str,
    password: str,
    verificator, # Async Callable[User, str]
    code: Optional[str] = None,
) -> Tuple[User, bool, str]:
    user = await User.get_or_none(username=username).prefetch_related("role")

    # USER EXISTS
    if not user:
        return {
            "user": None,
            "status": LoginStatusEnum.USER_NOT_FOUND,
        }

    # CORRECT PASSWORD
    is_password_correct = password_verify(password, user.password)
    if not is_password_correct:
        return {
            "user": None,
            "status": LoginStatusEnum.BAD_CREDENTIALS,
        }

    # ERGON VALIDATION
    is_employee = await employee_verify(user)
    if not is_employee:
        return {
            "user": user,
            "status": LoginStatusEnum.INACTIVE_EMPLOYEE,
        }

    # 2FA TOTP SENT
    if user.is_2fa_required and not code:
        return {
            "user": user,
            "status": LoginStatusEnum.REQUIRE_2FA,
        }

    # 2FA TOTP VALIDATION
    if user.is_2fa_required and code:
        is_2fa_valid = await verificator(user, code)
        if not is_2fa_valid:
            return {
                "user": user,
                "status": LoginStatusEnum.BAD_OTP,
            }

    return {
        "user": user,
        "status": LoginStatusEnum.SUCCESS,
    }


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create an access token.

    Args:
        data (dict): The data to encode into the token.
        expires_delta (timedelta, optional): The expiry time of the token.

    Returns:
        str: The encoded token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


def password_hash(password: str) -> str:
    """Hash a password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def password_verify(password: str, hashed: str) -> bool:
    """Verify a password against a hash.

    Args:
        password (str): The password to verify.
        hashed (str): The hashed password to verify against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(password, hashed)