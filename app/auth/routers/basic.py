# -*- coding: utf-8 -*-
import io
from typing import Annotated

from fastapi import Depends
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from loguru import logger

from app import config
from app.types import Token
from app.auth.utils import authenticate_user, generate_user_token
from app.auth.enums import LoginStatusEnum
from app.auth.types import AuthenticationErrorModel


router = APIRouter(prefix="/basic")

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
    logger.info(f"login_result: {login_result['status']}")

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