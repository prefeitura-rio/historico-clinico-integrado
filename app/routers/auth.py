# -*- coding: utf-8 -*-
import io
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from app.models import User
from app.types.pydantic_models import Token
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

    # Caso 1: Usuário não registrou 2FA e está tentando logar
    if user.is_2fa_required and not user.is_2fa_activated:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="2FA not activated. Use the /2fa/enable/ endpoint",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Caso 2: Usuário registrou 2FA e está tentando logar
    secret_key = await TwoFactorAuth.get_or_create_secret_key(user.id)
    two_factor_auth = TwoFactorAuth(user.id, secret_key)

    is_valid = two_factor_auth.verify_totp_code(totp_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": generate_user_token(user),
        "token_type": "bearer",
    }

@router.post("/2fa/enable/")
async def enable_2fa(
    current_user: Annotated[User, Depends(get_current_frontend_user)],
):
    secret_key = await TwoFactorAuth.get_or_create_secret_key(current_user.id)
    two_factor_auth = TwoFactorAuth(current_user.id, secret_key)

    return {
        "secret_key": two_factor_auth.secret_key
    }


@router.get("/2fa/activate/generate-qrcode/")
async def generate_qrcode(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
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


@router.post('/2fa/activate/verify-code/')
async def verify_code(
    totp_code: str,
    current_user: Annotated[User, Depends(get_current_frontend_user)],
):
    secret_key = await TwoFactorAuth.get_or_create_secret_key(current_user.id)
    two_factor_auth = TwoFactorAuth(current_user.id, secret_key)

    is_valid_totp = two_factor_auth.verify_totp_code(totp_code)

    if is_valid_totp:
        current_user.is_2fa_activated = True
        await current_user.save()

    return {
        'success': is_valid_totp
    }
