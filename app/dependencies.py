# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from tortoise.exceptions import ValidationError
import jwt
from jwt import PyJWTError

from app import config
from app.models import User
from app.types.pydantic_models import TokenData
from app.validators import CPFValidator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"JWT module error: {str(exc)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await User.get_or_none(username=token_data.username).prefetch_related(
        "role", "role__permition", "data_source"
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Username in Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

async def assert_user_has_pipeline_write_permition(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role.permition in [
        'pipeline_write',
        'pipeline_readwrite',
    ]:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User don't have permition to Write data into HCI",
    )

async def assert_user_has_pipeline_read_permition(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role.permition in [
        'pipeline_read',
        'pipeline_readwrite',
    ]:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User don't have permition to Read data from HCI",
    )

def assert_cpf_is_valid(cpf: str):
    validator = CPFValidator()
    try:
        validator(cpf)
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid CPF")

    return cpf