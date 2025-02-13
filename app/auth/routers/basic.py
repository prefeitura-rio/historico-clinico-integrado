# -*- coding: utf-8 -*-
import asyncio
from typing import Annotated

from fastapi import Depends
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from loguru import logger

from app import config
from app.models import User
from app.types import Token
from app.utils import send_email_to_created_user
from app.auth.utils import authenticate_user, generate_user_token, password_hash
from app.auth.enums import LoginStatusEnum
from app.auth.types import AuthenticationErrorModel, UserCreationModel


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

@router.post(
    "/create-user"
)
async def create_user(
    users : list[UserCreationModel]
):
    users_dict = [user.dict() for user in users]

    # --------------------------------------
    # Hash Password
    # --------------------------------------
    for user in users_dict:
        user['password'] = password_hash(user['password'])
    
    # --------------------------------------
    # Rename Cols
    # --------------------------------------
    for user in users_dict:
        user['data_source'] = user.pop('cnes')

    # --------------------------------------
    # Bulk Create
    # --------------------------------------
    users_to_create = []
    for user in users_dict:
        users_to_create.append(User(**user))

    try:
        await User.bulk_create(
            objects=users_to_create,
            on_conflict=['cpf','username']
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error During Bulk Insert"
            },
        )
    
    # --------------------------------------
    # Send Email
    # --------------------------------------
    awaitables = [
        send_email_to_created_user(
            name=user.name,
            username=user.username,
            password=user.password,
            email=user.email,
        )
        for user in users_to_create
    ]
    asyncio.gather(*awaitables)
    
    return {
        "success": True,
        "message": "Success"
    }
