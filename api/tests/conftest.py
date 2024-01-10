# -*- coding: utf-8 -*-
import asyncio

import pytest
from httpx import AsyncClient
from tortoise import Tortoise

from app.db import TORTOISE_ORM
from app.main import app
from app.models import City, Country, DataSource, State, User
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
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await City.all().delete()
    await Country.all().delete()
    await DataSource.all().delete()
    await Gender.all().delete()
    await State.all().delete()
    await User.all().delete()
    country = await Country.create(name="Brasil")
    state = await State.create(name="Rio de Janeiro", country=country)
    await City.create(name="Rio de Janeiro", state=state)
    ds = await DataSource.create(name="test_datasource")
    await Gender.create(slug="male", name="male")
    await User.create(
        username="pedro",
        email="pedro@example.com",
        password=password_hash("senha"),
        is_active=True,
        is_superuser=True,
        data_source=ds,
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
