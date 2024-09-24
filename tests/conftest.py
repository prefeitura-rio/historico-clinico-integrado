# -*- coding: utf-8 -*-
import asyncio
import pytest
import random
from httpx import AsyncClient
from tortoise import Tortoise

import scripts.database_init_table
import scripts.create_user

from app.db import TORTOISE_ORM
from app.main import app
from app.utils import read_bq, prepare_gcp_credential
from app.config import (
    BIGQUERY_PROJECT,
    BIGQUERY_PATIENT_HEADER_TABLE_ID,
    BIGQUERY_PATIENT_SUMMARY_TABLE_ID,
    BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID,
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client_object:
        yield client_object


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests(
    patient_cpf: str, other_patient_cpf: str, test_password: str
):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    await scripts.database_init_table.run()
    await scripts.create_user.create_any_user(
        username="pipeliner",
        password=test_password,
        cpf=patient_cpf,
        role="pipeliner",
        is_admin=False,
    )
    await scripts.create_user.create_any_user(
        username="frontend",
        password=test_password,
        cpf=other_patient_cpf,
        role="desenvolvedor",
        data_source="3567508",
        is_admin=False,
    )
    yield
    await Tortoise.close_connections()


@pytest.fixture(scope="session")
async def patient_cpf_with_data():
    prepare_gcp_credential()

    response = await read_bq(
        f"""
        WITH
            allowed_cpf AS (
                SELECT cpf
                FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_HEADER_TABLE_ID}
                WHERE exibicao.indicador = True
                ORDER BY RAND()
            ),
            cpf_with_summary AS (
                SELECT cpf
                FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_SUMMARY_TABLE_ID}
                WHERE
                    array_length(continuous_use_medications) > 0 or
                    array_length(allergies) > 0
                ORDER BY RAND()
            ),
            cpf_with_encounters AS (
                SELECT cpf
                FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID}
                WHERE exibicao.indicador = True
                ORDER BY RAND()
            )
        SELECT cpf
        FROM allowed_cpf
            INNER JOIN cpf_with_summary USING (cpf)
            INNER JOIN cpf_with_encounters USING (cpf)
        WHERE
            cpf in (SELECT cpf FROM cpf_with_summary) and
            cpf in (SELECT cpf FROM cpf_with_encounters)
        LIMIT 1
        """,
        from_file="/tmp/credentials.json",
    )
    cpf = response[0]["cpf"]
    yield cpf


@pytest.fixture(scope="session")
async def test_password():
    random_password = [random.choice("1234567890") for _ in range(3)]
    yield "".join(random_password)


@pytest.fixture(scope="session")
async def patient_cpf():
    yield "38965996074"


@pytest.fixture(scope="session")
async def patient_code():
    yield "38965996074.20210101"


@pytest.fixture(scope="session")
async def other_patient_cpf():
    yield "74663240020"


@pytest.fixture(scope="session")
async def other_patient_code():
    yield "74663240020.20210101"


@pytest.fixture(scope="session")
async def patient_invalid_cpf():
    yield "11111111111"


@pytest.fixture(scope="session")
async def patient_invalid_code():
    yield "11111111111.20210101"


@pytest.fixture(scope="session")
async def token_frontend(client: AsyncClient, test_password: str):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": "frontend", "password": test_password},
    )
    yield response.json().get("access_token")


@pytest.fixture(scope="session")
async def token_pipeline(client: AsyncClient, test_password: str):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": "pipeliner", "password": test_password},
    )
    yield response.json().get("access_token")
