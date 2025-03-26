# -*- coding: utf-8 -*-
import httpx
import base64
from fastapi import HTTPException, APIRouter
from loguru import logger


from app import config
from app.types import Token
from app.auth.types import LoginFormGovbr, AuthenticationErrorModel
from app.auth.utils import generate_token_from_user_data
from app.auth.utils.govbr import get_user_data_from_access_list, decode_token


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
    id_token = response_json.get("id_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Token de acesso não recebido.")
    
    logger.info(f"Fetching JWK from GovBR...")
    jwk_url = f"{config.GOVBR_PROVIDER_URL}/jwk"
    jwk_response = await fetch_with_retry("GET", jwk_url, timeout=10.0)
    
    logger.info(f"Decoding ID token...")
    payload_id_token = await decode_token(id_token, jwk_response)

    logger.info(f"Decoding Access token...")
    payload_access_token = await decode_token(access_token, jwk_response)

    # -----------------------------
    # LOGIN
    # -----------------------------
    cpf = payload_access_token.get('sub')
    email = payload_id_token.get('email', f"{cpf}@gov.br")

    logger.info(f"User: {cpf} ({email})")
    user_data = await get_user_data_from_access_list(cpf)

    if not user_data:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    user_data["email"] = email

    return {
        "access_token": generate_token_from_user_data(user_data),
        "token_type": "bearer",
        "token_expire_minutes": int(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
