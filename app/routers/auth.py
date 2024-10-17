# -*- coding: utf-8 -*-
import io
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse,JSONResponse

from app import config
from app.models import User
from app.types.frontend import LoginFormWith2FA, LoginForm
from app.types.pydantic_models import Token, Enable2FA
from app.utils import authenticate_user, generate_user_token, read_bq
from app.security import TwoFactorAuth
from app.dependencies import assert_user_is_active
from app.enums import LoginErrorEnum
from app.types.errors import (
    AuthenticationErrorModel
)
from app.config import (
    BIGQUERY_ERGON_TABLE_ID,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/token",
    response_model=Token,
    responses={
        401: {"model": AuthenticationErrorModel}
    }
)
async def login_without_2fa(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:

    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Incorrect Username or Password",
                "type": LoginErrorEnum.BAD_CREDENTIALS,
            },
        )

    if user.is_2fa_required:
        return JSONResponse(
            status_code=401,
            content={
                "message": "2FA required. Use the /2fa/login/ endpoint",
                "type": LoginErrorEnum.REQUIRE_2FA,
            },
        )

    return {
        "access_token": generate_user_token(user),
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }


@router.post(
    "/2fa/is-2fa-active/",
    response_model=bool,
    responses={
        401: {"model": AuthenticationErrorModel}
    },
)
async def is_2fa_active(
    form_data: LoginForm,
) -> bool:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Incorrect Username or Password",
                "type": LoginErrorEnum.BAD_CREDENTIALS,
            },
        )

    return user.is_2fa_activated


@router.post(
    "/2fa/login/",
    response_model=Token,
    responses={
        401: {"model": AuthenticationErrorModel}
    }
)
async def login_with_2fa(
    form_data: LoginFormWith2FA,
) -> Token:

    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Incorrect Username or Password",
                "type": LoginErrorEnum.BAD_CREDENTIALS,
            },
        )

    # ----------------------------------------
    # 2FA Verification
    # ----------------------------------------
    secret_key = await TwoFactorAuth.get_or_create_secret_key(user)
    two_factor_auth = TwoFactorAuth(user, secret_key)

    is_valid = two_factor_auth.verify_totp_code(form_data.totp_code)
    if not is_valid:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Incorrect OTP",
                "type": LoginErrorEnum.BAD_OTP,
            },
        )
    if not user.is_2fa_activated:
        user.is_2fa_activated = True
        await user.save()

    # ----------------------------------------
    # Validate access status in ERGON database
    # ----------------------------------------
    if user.is_ergon_validation_required:
        ergon_register = await read_bq(
            f"""
            SELECT *
            FROM {BIGQUERY_ERGON_TABLE_ID}
            WHERE cpf_particao = {user.cpf}
            """,
            from_file="/tmp/credentials.json",
        )
        # If has ERGON register and is an inactive employee: Unauthorized
        if len(ergon_register) > 0 and ergon_register[0].get("status_ativo", False) is False:
            return JSONResponse(
                status_code=401,
                content={
                    "message": "User is not an active employee",
                    "type": LoginErrorEnum.NOT_ACTIVE_EMPLOYEE,
                },
            )

    return {
        "access_token": generate_user_token(user),
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }


@router.post(
    "/2fa/enable/",
    response_model=Enable2FA,
    responses={
        400: {"model": str}
    }
)
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


@router.post(
    "/2fa/generate-qrcode/",
    response_model=bytes,
    responses={
        400: {"model": str},
        401: {"model": AuthenticationErrorModel},
        404: {"model": str}
    }
)
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
