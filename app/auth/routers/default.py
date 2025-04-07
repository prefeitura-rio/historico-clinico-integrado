# -*- coding: utf-8 -*-
from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt
import json
from app.models import User
from app.types import Token, TokenData
from app.config import base as config

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post(
    "/token",
    response_model=Token
)
async def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    vitacare_username = config.VITACARE_USERNAME

    if form_data.username != vitacare_username:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Incorrect Username or Password"
            },
        )

    is_password_correct = pwd_context.verify(form_data.password, config.VITACARE_HASHED_PASSWORD)

    if not is_password_correct:
        return JSONResponse(
            status_code=401,
            content={
                "message": "Incorrect Username or Password"
            },
        )

    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
        return encoded_jwt

    user = await User.get_or_none(username=vitacare_username)
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    access_token = create_access_token(
        data={"sub": TokenData(**dict(user)).json()},
        expires_delta=timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
