# -*- coding: utf-8 -*-
import io
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from app import config
from app.models import User
from app.types.frontend import LoginFormWith2FA, LoginForm
from app.types.pydantic_models import Token, Enable2FA
from app.utils import authenticate_user, generate_user_token, read_bq
from app.security import TwoFactorAuth
from app.dependencies import assert_user_is_active
from app.config import (
    BIGQUERY_ERGON_TABLE_ID,
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
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }


@router.post("/2fa/is-2fa-active/")
async def is_2fa_active(
    form_data: LoginForm,
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
    form_data: LoginFormWith2FA,
) -> Token:

    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    secret_key = await TwoFactorAuth.get_or_create_secret_key(user)
    two_factor_auth = TwoFactorAuth(user, secret_key)

    is_valid = two_factor_auth.verify_totp_code(form_data.totp_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_2fa_activated:
        user.is_2fa_activated = True
        await user.save()

    # ----------------------------------------
    # Validate access status in ERGON database
    # ----------------------------------------
    vinculo = read_bq(
        f"""
        SELECT *
        FROM {BIGQUERY_ERGON_TABLE_ID}
        WHERE cpf_particao = {user.cpf}
        """
    )
    # If the user is not in ERGON or is active in ERGON, generate a token
    if len(vinculo) == 0 or vinculo[0].get("status_ativo", False):
        return {
            "access_token": generate_user_token(user),
            "token_type": "bearer",
            "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not an active employee",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/2fa/enable/")
async def enable_2fa(
    current_user: Annotated[User, Depends(assert_user_is_active)],
) -> Enable2FA:
    if current_user.is_2fa_activated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA already enabled",
        )

    secret_key = await TwoFactorAuth.get_or_create_secret_key(current_user)
    two_factor_auth = TwoFactorAuth(current_user, secret_key)

    return {"secret_key": two_factor_auth.secret_key}


@router.post("/2fa/generate-qrcode/")
async def generate_qrcode(
    form_data: LoginForm,
) -> bytes:
    current_user = await authenticate_user(form_data.username, form_data.password)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if current_user.is_2fa_activated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA already activated using QR Code",
        )

    secret_key = await TwoFactorAuth.get_or_create_secret_key(current_user)
    two_factor_auth = TwoFactorAuth(current_user, secret_key)

    qr_code = two_factor_auth.qr_code
    if qr_code is None:
        raise HTTPException(status_code=404, detail="User not found")

    return StreamingResponse(io.BytesIO(qr_code), media_type="image/png")
