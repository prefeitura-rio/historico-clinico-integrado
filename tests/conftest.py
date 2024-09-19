# -*- coding: utf-8 -*-
import asyncio

import pytest
from httpx import AsyncClient
from tortoise import Tortoise

from app.db import TORTOISE_ORM
from app.main import app
from app.models import (
    DataSource,
    User,
    RawPatientRecord,
    RawPatientCondition,
    Occupation,
    OccupationFamily
)
from app.utils import password_hash, read_bq, prepare_gcp_credential
from app.config import (
    BIGQUERY_PROJECT,
    BIGQUERY_PATIENT_HEADER_TABLE_ID,
    BIGQUERY_PATIENT_SUMMARY_TABLE_ID,
    BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID
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
    other_patient_cpf: str,
    other_patient_code: str
):

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    datasource, _ = await DataSource.get_or_create(
        description="test_datasource",
        system="vitacare",
        cnes="1234567"
    )
    occupation_family, _ = await OccupationFamily.get_or_create(
        code="1114", defaults={"name": "Test occupation family"}
    )
    await Occupation.get_or_create(
        cbo="111415", defaults={
            "description": "Test occupation",
            "family": occupation_family
        }
    )
    pipeline_user = await User.get_or_none(username="pipeliner")
    if pipeline_user:
        await pipeline_user.delete()
    await User.update_or_create(
        username="pipeliner",
        email="test1@example.com",
        password=password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
        role_id="pipeliner",
        data_source=datasource,
    )
    frontend_user = await User.get_or_none(username="frontend")
    if frontend_user:
        await frontend_user.delete()
    await User.update_or_create(
        username="frontend",
        email="test2@example.com",
        password=password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
        role_id="desenvolvedor",
        data_source=datasource,
    )
    await RawPatientRecord.get_or_create(
        patient_cpf=other_patient_cpf,
        patient_code=other_patient_code,
        source_updated_at="2021-06-07T00:00:00Z",
        data={"name": "Maria"},
        data_source=datasource
    )
    await RawPatientCondition.get_or_create(
        patient_cpf=other_patient_cpf,
        patient_code=other_patient_code,
        source_updated_at="2021-06-07T00:00:00Z",
        data={"cid": "A001"},
        data_source=datasource
    )
    yield
    await Tortoise.close_connections()


@pytest.fixture(scope="session")
async def cpf_with_header():
    prepare_gcp_credential()

    response = await read_bq(f"""
        SELECT cpf
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_HEADER_TABLE_ID}
        WHERE exibicao.indicador = True
        ORDER BY RAND()
        LIMIT 1
        """,
        from_file="/tmp/credentials.json"
    )
    cpf = response[0]["cpf"]
    yield cpf

@pytest.fixture(scope="session")
async def cpf_with_summary():
    prepare_gcp_credential()

    response = await read_bq(f"""
        SELECT cpf
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_SUMMARY_TABLE_ID}
        WHERE
            array_length(continuous_use_medications) > 0 or
            array_length(allergies) > 0
        ORDER BY RAND()
        LIMIT 1
        """,
        from_file="/tmp/credentials.json"
    )
    cpf = response[0]["cpf"]
    yield cpf

@pytest.fixture(scope="session")
async def cpf_with_encounters():
    prepare_gcp_credential()

    response = await read_bq(f"""
        SELECT cpf
        FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID}
        WHERE exibicao.indicador = True
        ORDER BY RAND()
        LIMIT 1
        """,
        from_file="/tmp/credentials.json"
    )
    cpf = response[0]["cpf"]
    yield cpf


@pytest.fixture(scope="session")
async def password():
    yield "testpassword"


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
async def token_frontend(client: AsyncClient):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": "frontend", "password": "testpassword"},
    )
    yield response.json().get("access_token")

@pytest.fixture(scope="session")
async def token_pipeline(client: AsyncClient):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": "pipeline", "password": "testpassword"},
    )
    yield response.json().get("access_token")


@pytest.fixture(scope="session")
async def patientrecord_raw_source(patient_cpf: str):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    raw_patientrecord = await RawPatientRecord.get(
        patient_cpf=patient_cpf
    ).first()

    yield str(raw_patientrecord.id)


@pytest.fixture(scope="session")
async def patientcondition_raw_source(patient_cpf: str):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    raw_patientcondition = await RawPatientCondition.get(
        patient_cpf=patient_cpf
    ).first()
    yield str(raw_patientcondition.id)


@pytest.fixture(scope="session")
async def other_patientrecord_raw_source(other_patient_cpf: str):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    raw_patientrecord = await RawPatientRecord.get(
        patient_cpf=other_patient_cpf
    ).first()

    yield str(raw_patientrecord.id)


@pytest.fixture(scope="session")
async def other_patientcondition_raw_source(other_patient_cpf: str):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    raw_patientcondition = await RawPatientCondition.get(
        patient_cpf=other_patient_cpf
    ).first()

    yield str(raw_patientcondition.id)
