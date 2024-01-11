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

@pytest.mark.anyio
@pytest.mark.run(order=2)
async def test_get_patient(client: AsyncClient, token: str, patient_cpf : str):
    response = await client.get(
        f"/mrg/patient/{patient_cpf}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert 'gender' in response.json()
    assert 'nationality' in response.json()
    assert 'race' in response.json()
    assert 'birth_city' in response.json()
    assert 'birth_state' in response.json()
    assert 'birth_country' in response.json()
    assert 'address_list' in response.json()
    assert 'telecom_list' in response.json()
    assert 'condition_list' in response.json()
    assert 'cns_list' in response.json()