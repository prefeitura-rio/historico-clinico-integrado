# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, "../")

import pytest  # noqa
from httpx import AsyncClient  # noqa

from .utils import generate_cns, generate_cpf  # noqa


@pytest.mark.anyio
@pytest.mark.run(order=1)
async def test_auth(client: AsyncClient, username: str, password: str):
    response = await client.post(
        "/auth/token",
        headers={"content-type": "application/x-www-form-urlencoded"},
        data={"username": username, "password": password},
    )

    status_code = response.status_code
    assert status_code == 200

    result_body = response.json()
    assert "access_token" in result_body.keys()

    return result_body.get("access_token")