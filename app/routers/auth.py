# -*- coding: utf-8 -*-
import io
from datetime import timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from app import config
from app.models import User
from app.types.pydantic_models import Token
from app.utils import authenticate_user, create_access_token
from app.security import TwoFactorAuth
from app.dependencies import (
    get_current_frontend_user
)


router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:

    user: User = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/2fa/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    totp_code: Optional[str] = None,
) -> Token:

    user: User = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # IF 2FA is not Enabled
    is_2fa_disabled = user.secret_key is None
    is_trying_2fa = totp_code is not None

    # If 2FA is enabled and user is initializing the session
    if not is_2fa_disabled and not is_trying_2fa:
        # User must provide a OTP
        return {
            "2fa_enabled": True
        }

    # If 2FA is enabled and user is trying to login with OTP
    if is_trying_2fa and not is_2fa_disabled:
        secret_key = await TwoFactorAuth.get_or_create_secret_key(user.id)
        two_factor_auth = TwoFactorAuth(user.id, secret_key)

        is_valid = two_factor_auth.verify_totp_code(totp_code)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect OTP",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # If 2FA is disabled
    if is_2fa_disabled:
        is_valid = True

    # Generate Token
    access_token_expires = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "2fa_enabled": False,
        "access_token": access_token,
        "token_type": "bearer"
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


@router.get("/2fa/generate-qr/")
async def generate_qr(
    current_user: Annotated[User, Depends(get_current_frontend_user)],
):
    secret_key = await TwoFactorAuth.get_or_create_secret_key(current_user.id)
    two_factor_auth = TwoFactorAuth(current_user.id, secret_key)

    qr_code = two_factor_auth.qr_code
    if qr_code is None:
        raise HTTPException(status_code=404, detail="User not found")

    return StreamingResponse(io.BytesIO(qr_code), media_type="image/png")