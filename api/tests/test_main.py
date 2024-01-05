# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "../")

from app.main import app
from fastapi.testclient import TestClient

import random

def generate_cpf():
    cpf = [random.randint(0, 9) for x in range(9)]

    for _ in range(2):
        val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11

        cpf.append(11 - val if val > 1 else 0)

    cpf = [str(x) for x in cpf]

    return ''.join(cpf)

def generate_cns():
    cns = [random.randint(0, 16) for x in range(9)]
    cns = [str(x) for x in cns]

    return ''.join(cns)


def test_auth():
    with TestClient(app) as client:
        response = client.post(
            "/auth/token/",
            headers={
                "content-type": "application/x-www-form-urlencoded"
            },
            data={
                'username':'pedro',
                'password':'senha'
            }
        )

    status_code = response.status_code
    assert status_code == 200

    result_body = response.json()
    assert 'access_token' in result_body.keys()

    return result_body.get('access_token')

def test_patient_creation__minimal():
    token = test_auth()
    random_cpf = generate_cpf()

    with TestClient(app) as client:

        response = client.post(
            "/patients/",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "active": True,
                "birth_date": "1999-12-20",
                "gender": "male",
                "cpf": random_cpf,
                "name": "MANUEL GOMES",
                "telecom":  [{
                    "value": "5521123456789"
                }]
            }
        )
    assert response.status_code == 201
    assert response.json() != None
    assert 'cpf' in response.json()
    assert response.json()['cpf'] == random_cpf

def test_patient_creation__complete():
    token = test_auth()
    random_cpf = generate_cpf()
    random_cns = generate_cns()

    with TestClient(app) as client:

        response = client.post(
            "/patients/",
            headers={
                "Authorization": f"Bearer {token}"
            },
            json={
                "active": True,
                "address": [{
                    "use": "home",
                    "type": "physical",
                    "line": "AV SQN BLOCO M 604 APARTAMENTO ASA NORTE",
                    "city": "Rio de Janeiro",
                    "state": "Rio de Janeiro",
                    "country": "Brasil",
                    "postal_code": "70752130",
                    "period": {
                        "start": "2020-10-01 00:00:00",
                        "end": "2020-10-02 00:00:00"
                        }
                }],
                "birth_city": "Rio de Janeiro",
                "birth_country": "Brasil",
                "birth_state": "Rio de Janeiro",
                "birth_date": "1999-12-20 00:00:00",
                "deceased": False,
                "gender": "male",
                "cpf": random_cpf,
                "cns": random_cns,
                "name": "GABRIELA INACIO ALVES",
                "nationality": "B",
                "naturalization": "",
                "mother": "MARILIA FARES DA ROCHA ALVES",
                "father": "JURACY ALVES",
                "protected_person": False,
                "race": "Parda",
                "ethnicity": "PATAXO",
                "telecom":  [{
                    "system": "phone",
                    "use": "home",
                    "value": "5521123456789",
                    "rank": "1",
                    "period": {
                        "start": "2020-10-01 00:00:00",
                        "end": "2020-10-02 00:00:00"
                        }
                    }]
            }
        )
    assert response.status_code == 201
    assert response.json() != None
    assert 'cpf' in response.json()
    assert response.json()['cpf'] == random_cpf