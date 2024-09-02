# -*- coding: utf-8 -*-
import io
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from app.models import User
from app.types.pydantic_models import Token, Enable2FA
from app.utils import authenticate_user, generate_user_token
from app.security import TwoFactorAuth
from app.dependencies import (
    get_current_frontend_user
)


router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/token")
async def login_without_2fa(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:

    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_2fa_required:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="2FA required. Use the /2fa/login/ endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": generate_user_token(user),
        "token_type": "bearer"
    }


@router.post("/2fa/is-2fa-active/")
async def is_2fa_active(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> bool:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user.is_2fa_activated


@router.post("/2fa/login/")
async def login_with_2fa(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    totp_code: str,
) -> Token:

    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    secret_key = await TwoFactorAuth.get_or_create_secret_key(user.id)
    two_factor_auth = TwoFactorAuth(user.id, secret_key)

    is_valid = two_factor_auth.verify_totp_code(totp_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_2fa_activated:
        user.is_2fa_activated = True
        await user.save()

    return {
        "access_token": generate_user_token(user),
        "token_type": "bearer",
    }


@router.post("/2fa/enable/")
async def enable_2fa(
    current_user: Annotated[User, Depends(get_current_frontend_user)],
) -> Enable2FA:
    secret_key = await TwoFactorAuth.get_or_create_secret_key(current_user.id)
    two_factor_auth = TwoFactorAuth(current_user.id, secret_key)

    return {
        "secret_key": two_factor_auth.secret_key
    }


@router.post("/2fa/generate-qrcode/")
async def generate_qrcode(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> bytes:
    current_user = await authenticate_user(form_data.username, form_data.password)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    secret_key = await TwoFactorAuth.get_or_create_secret_key(current_user.id)
    two_factor_auth = TwoFactorAuth(current_user.id, secret_key)

    qr_code = two_factor_auth.qr_code
    if qr_code is None:
        raise HTTPException(status_code=404, detail="User not found")

    return StreamingResponse(io.BytesIO(qr_code), media_type="image/png")
