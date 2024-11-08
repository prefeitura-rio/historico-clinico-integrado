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
from app.enums import LoginStatusEnum
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

    login_result = await authenticate_user(form_data.username, form_data.password)

    if login_result['status'] != LoginStatusEnum.SUCCESS:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Something went wrong",
                "type": login_result['status'],
            },
        )

    return {
        "access_token": generate_user_token(login_result['user']),
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
    login_result = await authenticate_user(form_data.username, form_data.password)

    if login_result['status'] in [
        LoginStatusEnum.USER_NOT_FOUND,
        LoginStatusEnum.BAD_CREDENTIALS,
        LoginStatusEnum.INACTIVE_EMPLOYEE,
    ]:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Something went wrong",
                "type": login_result['status'],
            },
        )
    
    return login_result['user'].is_2fa_activated


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

    login_result = await authenticate_user(
        form_data.username, 
        form_data.password,
        form_data.totp_code,
    )
    
    if login_result['status'] == LoginStatusEnum.SUCCESS:
        login_result['user'].is_2fa_activated = True
        await login_result['user'].save()

        return {
            "access_token": generate_user_token(login_result['user']),
            "token_type": "bearer",
            "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
    else:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Something went wrong",
                "type": login_result['status'],
            },
        )


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
    login_result = await authenticate_user(form_data.username, form_data.password)

    
    if login_result['status'] in [
        LoginStatusEnum.USER_NOT_FOUND,
        LoginStatusEnum.BAD_CREDENTIALS,
        LoginStatusEnum.INACTIVE_EMPLOYEE,
    ]:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Something went wrong",
                "type": login_result['status'],
            },
        )

    if login_result['user'].is_2fa_activated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA already activated using QR Code",
        )

    secret_key = await TwoFactorAuth.get_or_create_secret_key(login_result['user'])
    two_factor_auth = TwoFactorAuth(login_result['user'], secret_key)

    qr_code = two_factor_auth.qr_code
    if qr_code is None:
        raise HTTPException(status_code=404, detail="User not found")

    return StreamingResponse(io.BytesIO(qr_code), media_type="image/png")
