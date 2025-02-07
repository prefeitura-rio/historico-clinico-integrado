# -*- coding: utf-8 -*-
import httpx
import jwt
import base64
from fastapi import HTTPException
from fastapi import APIRouter
from loguru import logger

from app import config
from app.models import User
from app.types import Token
from app.utils import employee_verify
from app.auth.types import LoginFormGovbr
from app.auth.types import AuthenticationErrorModel
from app.auth.utils import generate_user_token


router = APIRouter(prefix="/govbr")

@router.post(
    "/login/",
    response_model=Token,
    responses={
        401: {"model": AuthenticationErrorModel}
    },
)
async def login_with_govbr(
    form_data: LoginFormGovbr,
) -> Token:
    
    # -----------------------------
    # GET THE ACCESS TOKEN
    # -----------------------------
    authorization_b64 = base64.b64encode(f"{config.GOVBR_CLIENT_ID}:{config.GOVBR_CLIENT_SECRET}".encode()).decode()
    url = f"{config.GOVBR_PROVIDER_URL}/token"
    logger.info(f"Connecting with GOV.BR to retrieve token: {url}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {authorization_b64}",
            },

            data={
                "grant_type": "authorization_code",
                "code": form_data.code,
                "redirect_uri": config.GOVBR_REDIRECT_URL,
                "code_verifier": form_data.code_verifier,
            },
        )
    response_json = response.json()
    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail=f"Erro ao obter o token de acesso: {response_json['error_description']}"
        )

    access_token = response_json['access_token']

    # -----------------------------
    # VALIDATE THE ID_TOKEN
    # -----------------------------

    # Get keys from the jwk endpoint
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.GOVBR_PROVIDER_URL}/jwk",
        )
    response_json = response.json()

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Erro ao obter as chaves do JWK") 
       
    key = response_json['keys'][0]

    # Validate the id_token
    try:
        payload = jwt.decode(access_token, key['n'], algorithms=["RS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")


    # -----------------------------
    # LOGIN
    # -----------------------------
    name, cpf = payload['name'], payload['sub']
    user = await User.objects.get_or_none(cpf=cpf)

    if not user:
        # TODO: Create a new user
        raise HTTPException(status_code=401, detail=f"User {name} not found with this CPF {cpf}")

    is_employee = await employee_verify(user)
    if not is_employee:
        raise HTTPException(status_code=401, detail=f"User {name} is not an employee")

    return {
        "access_token": generate_user_token(user),
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }


