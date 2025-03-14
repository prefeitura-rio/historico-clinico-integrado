# -*- coding: utf-8 -*-
import json
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt

from app import config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_token_from_user_data(user_data: dict) -> str:
    """
    Generates a JWT access token for a given user.
    Args:
        user_data (dict): The user data for which the token is being generated.
    Returns:
        str: The generated JWT access token.
    """

    access_token_expires = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": json.dumps(user_data)}, expires_delta=access_token_expires
    )

    return access_token


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