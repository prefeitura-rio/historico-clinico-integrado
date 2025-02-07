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
    authorization_b64 = base64.b64encode(
        f"{config.GOVBR_CLIENT_ID}:{config.GOVBR_CLIENT_SECRET}".encode()).decode()

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

    # Obtém o payload sem validar ainda (para extrair o 'kid')
    try:
        unverified_header = jwt.get_unverified_header(access_token)
        key_id = unverified_header.get("kid")  # Obtém o ID da chave
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token inválido, cabeçalho não pode ser lido")

    # Get keys from the jwk endpoint
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{config.GOVBR_PROVIDER_URL}/jwk", timeout=10.0)
    except (httpx.ConnectError, httpx.ReadTimeout) as e:
        logger.error(f"Erro de conexão ao obter JWK: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter as chaves do JWK")

    response_json = response.json()
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao obter as chaves do JWK")

    # Escolhe a chave correta pelo 'kid'
    matching_key = None
    for jwk_key in response_json['keys']:
        if jwk_key["kid"] == key_id:
            matching_key = jwk_key
            break

    if not matching_key:
        raise HTTPException(
            status_code=500, detail="Nenhuma chave correspondente ao token encontrado no JWK")

    # Converte a JWK para chave pública RSA
    try:
        public_key = RSAAlgorithm.from_jwk(matching_key)
    except Exception as e:
        logger.error(f"Erro ao processar a JWK: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar a chave pública do JWK")

    # Valida o token com os parâmetros do provedor
    try:
        payload = jwt.decode(
            access_token,
            public_key,
            algorithms=["RS256"],
            audience=config.GOVBR_CLIENT_ID,  # Garante que o token seja para este cliente
            issuer=f"{config.GOVBR_PROVIDER_URL}/",  # Valida o emissor do token
            leeway=30  # Adiciona margem de 30s para evitar problemas de clock skew
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=500, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=500, detail=f"Token inválido: {str(e)}")

    # -----------------------------
    # LOGIN
    # -----------------------------
    cpf = payload.get('sub')
    if not cpf:
        raise HTTPException(status_code=401, detail="CPF não encontrado no token")

    user = await User.objects.get_or_none(cpf=cpf)
    if not user:
        raise HTTPException(
            status_code=401, detail=f"Usuário com CPF {cpf} não encontrado.")

    is_employee = await employee_verify(user)
    if not is_employee:
        raise HTTPException(
            status_code=401, detail=f"Usuário com CPF {cpf} não é um funcionário autorizado.")

    return {
        "access_token": generate_user_token(user),
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
