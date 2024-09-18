# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from app import config
from app.models import User
from app.types.pydantic_models import TokenData
from jwt import PyJWTError

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

    user = await User.get_or_none(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Username in Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def get_current_pipeline_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.is_superuser:
        return current_user

    if not current_user.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have a role")

    user_with_role = await User.get(id=current_user.id).prefetch_related("user_role")
    role = user_with_role.role

    if role.type.value in ["pipeline_user"]:
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User don't have permition to access Pipeline Endpoints",
        )


async def get_current_frontend_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.is_superuser:
        return current_user

    if not current_user.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User don't have a role")

    user_with_role = await User.get(id=current_user.id).prefetch_related("user_role")
    role = user_with_role.role

    if role.type.value in ["frontend_user"]:
        return current_user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User don't have permition to access Frontend Endpoints",
        )


async def is_superuser(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.is_superuser:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User don't have permition to access this endpoint",
    )
