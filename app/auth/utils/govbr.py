# -*- coding: utf-8 -*-

from loguru import logger
from app.config import (
    BIGQUERY_ACCESS_TABLE_ID,
)
from app.utils import read_bq


async def get_user_data(cpf: str) -> dict:

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

    registry = user_infos[0]
    return {
        "username": registry["cpf"],
        "name": registry["nome_completo"],
        "cpf": registry["cpf"],
        "job_title": registry["funcao_detalhada"],
        "access_level": registry["nivel_acesso"],
        "cnes": registry["unidade_cnes"],
        "ap": registry["unidade_ap"],
    }