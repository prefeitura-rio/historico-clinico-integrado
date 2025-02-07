# -*- coding: utf-8 -*-
import httpx
import jwt
import base64
from fastapi import HTTPException
from fastapi import APIRouter
from loguru import logger
from jwt.algorithms import RSAAlgorithm

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

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{config.GOVBR_PROVIDER_URL}/token",
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
                timeout=10.0,
            )
    except (httpx.ConnectError, httpx.ReadTimeout) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conectar com o endpoint de autenticação: {config.GOVBR_PROVIDER_URL}/token"
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
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{config.GOVBR_PROVIDER_URL}/jwk", timeout=10.0)
    except (httpx.ConnectError, httpx.ReadTimeout) as e:
        logger.error(f"Erro de conexão ao obter JWK: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter as chaves do JWK")

    response_json = response.json()
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Erro ao obter as chaves do JWK") 

    # Extrai a chave pública do JWK
    try:
        jwk_key = response_json['keys'][0]  # Pegamos a primeira chave (depende do provedor)
        public_key = RSAAlgorithm.from_jwk(jwk_key)  # Converte a JWK para RSA
    except Exception as e:
        logger.error(f"Erro ao processar a JWK: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar a chave pública do JWK")

    # Validate the id_token
    try:
        payload = jwt.decode(access_token, public_key, algorithms=["RS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
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


