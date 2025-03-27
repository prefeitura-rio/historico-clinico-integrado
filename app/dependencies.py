# -*- coding: utf-8 -*-
from typing import Annotated
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from tortoise.exceptions import ValidationError
import jwt
from jwt import PyJWTError
from loguru import logger

from app import config
from app.models import User
from app.types import TokenData
from app.validators import CPFValidator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user_data: str = payload.get("sub")
        user_data = json.loads(user_data)
        token_data = TokenData(**user_data)
    except PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"JWT module error: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error decoding token: {str(exc)}",
        ) from exc

    # Check if user exists
    user = await User.get_or_none(username=token_data.username)

    # Update user
    if user:
        logger.info(f"User {user.username} found in database")
        user.name = token_data.name
        user.cpf = token_data.cpf
        user.access_level = token_data.access_level
        user.cnes = token_data.cnes
        user.job_title = token_data.job_title
        user.ap = token_data.ap
        await user.save()
        return user

    # Create user
    try:
        user = await User.create(
            username=token_data.username,
            name=token_data.name,
            email=token_data.email,
            job_title=token_data.job_title,
            cpf=token_data.cpf,
            access_level=token_data.access_level,
            cnes=token_data.cnes,
            ap=token_data.ap,
        )
        logger.info(f"User {user.username} created in database")
    except Exception as exc:
        logger.error(f"Error creating user: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error creating user: {str(exc)}",
        ) from exc

    return user

async def assert_user_is_active(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def assert_user_is_superuser(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.is_superuser:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User don't have permition to access this endpoint",
    )

def assert_cpf_is_valid(cpf: str):
    validator = CPFValidator()
    try:
        validator(cpf)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid CPF")

    return cpf