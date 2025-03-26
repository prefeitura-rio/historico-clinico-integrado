# -*- coding: utf-8 -*-
import httpx
import jwt
import base64
from fastapi import HTTPException, APIRouter
from loguru import logger
from jwt.algorithms import RSAAlgorithm

from app import config
from app.types import Token
from app.auth.types import LoginFormGovbr, AuthenticationErrorModel
from app.auth.utils import generate_token_from_user_data
from app.auth.utils.govbr import get_user_data


router = APIRouter(prefix="/govbr")

retry_transport = httpx.AsyncHTTPTransport(retries=3)

async def fetch_with_retry(method, url, **kwargs):
    """Executa uma requisição HTTP com retry nativo do httpx."""
    async with httpx.AsyncClient(transport=retry_transport) as client:
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP {e.response.status_code} ao acessar {url}: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Erro ao acessar GovBR: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Erro na requisição ao GovBR ({url}): {e}")
            raise HTTPException(status_code=500, detail="Falha na comunicação com GovBR. Tente novamente.")

@router.post(
    "/login/",
    response_model=Token,
    responses={401: {"model": AuthenticationErrorModel}},
)
async def login_with_govbr(form_data: LoginFormGovbr) -> Token:
    # -----------------------------
    # GET THE ACCESS TOKEN
    # -----------------------------
    authorization_b64 = base64.b64encode(
        f"{config.GOVBR_CLIENT_ID}:{config.GOVBR_CLIENT_SECRET}".encode()
    ).decode()

    token_url = f"{config.GOVBR_PROVIDER_URL}/token"
    token_data = {
        "grant_type": "authorization_code",
        "code": form_data.code,
        "redirect_uri": config.GOVBR_REDIRECT_URL,
        "code_verifier": form_data.code_verifier,
    }
    token_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {authorization_b64}",
    }

    response_json = await fetch_with_retry("POST", token_url, headers=token_headers, data=token_data, timeout=10.0)
    access_token = response_json.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Token de acesso não recebido.")

    # -----------------------------
    # VALIDATE THE ID_TOKEN
    # -----------------------------
    try:
        unverified_header = jwt.get_unverified_header(access_token)
        key_id = unverified_header.get("kid")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Token inválido, cabeçalho não pode ser lido")

    # Obtém as chaves JWK do provedor GovBR
    jwk_url = f"{config.GOVBR_PROVIDER_URL}/jwk"
    jwk_response = await fetch_with_retry("GET", jwk_url, timeout=10.0)

    # Encontra a chave correta pelo 'kid'
    matching_key = next((key for key in jwk_response['keys'] if key["kid"] == key_id), None)
    if not matching_key:
        raise HTTPException(status_code=500, detail="Nenhuma chave correspondente ao token encontrada no JWK")

    # Converte a JWK para chave pública RSA
    try:
        public_key = RSAAlgorithm.from_jwk(matching_key)
    except Exception as e:
        logger.error(f"Erro ao processar a JWK: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar a chave pública do JWK")

    # Valida o token
    try:
        payload = jwt.decode(
            access_token,
            public_key,
            algorithms=["RS256"],
            audience=config.GOVBR_CLIENT_ID,
            issuer=f"{config.GOVBR_PROVIDER_URL}/",
            leeway=30,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

    # -----------------------------
    # LOGIN
    # -----------------------------
    cpf = payload.get('sub')
    if not cpf:
        raise HTTPException(status_code=401, detail="CPF não encontrado no token")

    user_data = await get_user_data(cpf)
    if not user_data:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    user_data["email"] = payload.get('email', f"{cpf}@gov.br")

    return {
        "access_token": generate_token_from_user_data(user_data),
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
