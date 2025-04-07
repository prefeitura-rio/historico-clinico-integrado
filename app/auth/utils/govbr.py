# -*- coding: utf-8 -*-
import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import HTTPException
from loguru import logger

from app.config import (
    BIGQUERY_ACCESS_TABLE_ID,
)
from app.utils import read_bq
from app import config


async def get_user_data_from_access_list(cpf: str) -> dict:

    user_infos = await read_bq(
        f"""
        SELECT *
        FROM {BIGQUERY_ACCESS_TABLE_ID}
        WHERE cpf_particao = {int(cpf)}
        LIMIT 1
        """,
        from_file="/tmp/credentials.json",
    )
    if len(user_infos) == 0:
        logger.info(f"User {cpf} not found in Database")
        return None

    logger.info(f"User {cpf} found in Database")

    registry = user_infos[0]
    return {
        "username": registry["cpf"],
        "name": registry["nome_completo"],
        "cpf": registry["cpf"],
        "access_level": registry["nivel_acesso"],
        "job_title": registry["funcao_detalhada"],
        "cnes": registry["unidade_cnes"],
        "ap": registry["unidade_ap"],
    }

async def decode_token(token: str, jwk_response: dict) -> dict:
    logger.debug(f"Getting key id from token...")
    try:
        unverified_header = jwt.get_unverified_header(token)
        key_id = unverified_header.get("kid")
    except jwt.DecodeError:
        logger.error(f"Token inválido, cabeçalho não pode ser lido")
        raise HTTPException(status_code=401, detail="Token inválido, cabeçalho não pode ser lido")

    logger.debug(f"Finding matching key in JWK...")
    matching_key = next((key for key in jwk_response['keys'] if key["kid"] == key_id), None)
    if not matching_key:
        logger.error(f"Nenhuma chave correspondente ao token encontrada no JWK")
        raise HTTPException(status_code=500, detail="Nenhuma chave correspondente ao token encontrada no JWK")

    logger.debug(f"Converting JWK to public key...")
    try:
        public_key = RSAAlgorithm.from_jwk(matching_key)
    except Exception as e:
        logger.error(f"Erro ao processar a JWK: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao processar a chave pública do JWK")

    logger.debug(f"Decoding token...")
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=config.GOVBR_CLIENT_ID,
            issuer=f"{config.GOVBR_PROVIDER_URL}/",
            leeway=30,
        )
    except jwt.ExpiredSignatureError:
        logger.error(f"Token expirado")
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        logger.error(f"Token inválido: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

    logger.debug(f"Token decoded successfully")
    return payload