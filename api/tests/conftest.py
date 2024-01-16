# -*- coding: utf-8 -*-
import asyncio

import pytest
from httpx import AsyncClient
from tortoise import Tortoise

from app.db import TORTOISE_ORM
from app.main import app
from app.models import City, Country, DataSource, State, User, Gender, Patient, \
    ConditionCode, PatientCondition, PatientCns, Race, Nationality, PatientAddress, PatientTelecom, \
    RawPatientRecord, RawPatientCondition
from app.utils import password_hash


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
async def initialize_tests(patient_cpf: str):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    await City.all().delete()
    await Country.all().delete()
    await DataSource.all().delete()
    await Gender.all().delete()
    await Race.all().delete()
    await Nationality.all().delete()
    await State.all().delete()
    await User.all().delete()
    await Patient.all().delete()
    await ConditionCode.all().delete()
    await PatientCondition.all().delete()
    await PatientCns.all().delete()
    await PatientAddress.all().delete()
    await PatientTelecom.all().delete()

    datasource  = await DataSource.create(
        description="test_datasource",
        system="vitacare",
        cnes="1234567"
    )
    country     = await Country.create(name="Brasil", code="00001")
    state       = await State.create(name="Rio de Janeiro", country=country, code="00001")
    city        = await City.create(name="Rio de Janeiro", state=state, code="00001")
    gender      = await Gender.create(slug="male", name="male")
    race        = await Race.create(slug="parda", name="parda")
    nationality = await Nationality.create(slug="B", name="B")

    await User.create(
        username="pedro",
        email="pedro@example.com",
        password=password_hash("senha"),
        is_active=True,
        is_superuser=True,
        data_source=datasource,
    )
    patient = await Patient.create(
        name="Pedro",
        patient_cpf=patient_cpf,
        birth_date="2021-01-01",
        active=True,
        protected_person=False,
        deceased=False,
        deceased_date=None,
        mother_name="Maria",
        father_name="João",
        nationality=nationality,
        race=race,
        birth_city=city,
        gender=gender
    )
    await PatientCns.create(
        value="123456789012345",
        patient=patient,
        is_main=True,
    )
    await PatientAddress.create(
        patient=patient,
        city=city,
        state=state,
        country=country,
        postal_code="00000000",
        line="Rua 1",
        type="home",
        use="home",
        period_start="2021-01-01"
    )
    await PatientTelecom.create(
        patient=patient,
        system="phone",
        use="home",
        value="21999999999",
        period_start="2021-01-01"
    )
    code = await ConditionCode.create(
        value="A001",
        type="cid",
        description="Teste"
    )
    await PatientCondition.create(
        patient=patient,
        condition_code=code,
        clinical_status="resolved",
        category="encounter-diagnosis",
        date="2021-01-01"
    )
    yield
    await Tortoise.close_connections()


@pytest.fixture(scope="session")
async def username():
    yield "pedro"


@pytest.fixture(scope="session")
async def email():
    yield "pedro@example.com"


@pytest.fixture(scope="session")
async def password():
    yield "senha"

@pytest.fixture(scope="session")
async def patient_cpf():
    yield "1111111111"

@pytest.fixture(scope="session")
async def token(client: AsyncClient, username: str, password: str):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": username, "password": password},
    )
    yield response.json().get("access_token")

@pytest.fixture(scope="session")
async def patientrecord_raw_source():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    raw_patientrecord = await RawPatientRecord.first()

    yield str(raw_patientrecord.id)

@pytest.fixture(scope="session")
async def patientcondition_raw_source():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    raw_patientcondition = await RawPatientCondition.first()

    yield str(raw_patientcondition.id)
