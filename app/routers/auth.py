# -*- coding: utf-8 -*-
import io
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from app import config
from app.models import User
from app.types.pydantic_models import Token
from app.utils import authenticate_user, create_access_token
from app.security import TwoFactorAuth, get_two_factor_auth


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


@router.post("/enable-2fa/{user_id}")
async def enable_2fa(
    two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth)
):
    return {
        "secret_key": two_factor_auth.secret_key
    }


@router.get("/generate-qr/{user_id}")
async def generate_qr(
    two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth)
):
    qr_code = two_factor_auth.qr_code
    if qr_code is None:
        raise HTTPException(status_code=404, detail="User not found")

    return StreamingResponse(io.BytesIO(qr_code), media_type="image/png")


@router.post("/verify-totp/{user_id}")
async def verify_totp(
    totp_code: str,
    two_factor_auth: TwoFactorAuth = Depends(get_two_factor_auth),
):
    is_valid = two_factor_auth.verify_totp_code(totp_code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Code invalid")
    return {
        "valid": is_valid
    }
