# -*- coding: utf-8 -*-
import hashlib
import json
import os
import base64

from google.cloud import bigquery
from google.oauth2 import service_account
from asyncer import asyncify
from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse
from app.models import User
from app.enums import AccessErrorEnum
from app.config import (
    BIGQUERY_PROJECT,
    BIGQUERY_PATIENT_HEADER_TABLE_ID,
    BIGQUERY_ERGON_TABLE_ID,
)


async def employee_verify(user: User) -> bool:
    if not user.is_ergon_validation_required:
        return True

    ergon_register = await read_bq(
        f"""SELECT * FROM {BIGQUERY_ERGON_TABLE_ID} WHERE cpf_particao = {user.cpf}""",
        from_file="/tmp/credentials.json",
    )
    if len(ergon_register) == 0 or len(ergon_register[0]["dados"]) == 0:
        logger.info(f"User {user.username} not found in Ergon")
        return False

    dado = ergon_register[0]['dados'][0]
    if dado["status_ativo"] is False:
        return False
    else:
        return True


def generate_dictionary_fingerprint(dict_obj: dict) -> str:
    """
    Generate a fingerprint for a dictionary object.

    Args:
        dict_obj (dict): The dictionary object to generate the fingerprint for.

    Returns:
        str: The MD5 hash of the serialized dictionary object.

    """
    serialized_obj = json.dumps(dict_obj, sort_keys=True)
    return hashlib.md5(serialized_obj.encode("utf-8")).hexdigest()


def prepare_gcp_credential() -> None:
    """
    Prepares Google Cloud Platform (GCP) credentials for use by decoding a base64
    encoded credential string from an environment variable and writing it to a
    temporary file. The path to this file is then set as the value of the
    GOOGLE_APPLICATION_CREDENTIALS environment variable.
    Environment Variables:
    - BASEDOSDADOS_CREDENTIALS_PROD: A base64 encoded string containing the GCP
      credentials.
    - GOOGLE_APPLICATION_CREDENTIALS: The path to the temporary file where the
      decoded credentials are stored.
    Returns:
    None
    """

    base64_credential = os.environ["BASEDOSDADOS_CREDENTIALS_PROD"]

    # Create tmp directory if it doesn't exist
    os.makedirs("/tmp", exist_ok=True)

    with open("/tmp/credentials.json", "wb") as f:
        f.write(base64.b64decode(base64_credential))


    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
    return


async def read_bq(query, from_file="/tmp/credentials.json"):
    """
    Asynchronously reads data from Google BigQuery using a provided SQL query.
    Args:
        query (str): The SQL query to execute on BigQuery.
        from_file (str, optional): The path to the service account credentials JSON file.
            Defaults to "/tmp/credentials.json".
    Returns:
        list: A list of dictionaries, where each dictionary represents a row from the query result.
    """

    logger.debug(
        f"""Reading BigQuery with query (QUERY_PREVIEW_ENABLED={
        os.environ['QUERY_PREVIEW_ENABLED']
    }): {query}"""
    )

    logger.info(f"Querying BigQuery: {query}")

    def execute_job():
        credentials = service_account.Credentials.from_service_account_file(
            from_file,
        )
        client = bigquery.Client(credentials=credentials)
        row_iterator = client.query_and_wait(query)
        return [dict(row) for row in row_iterator]

    rows = await asyncify(execute_job)()

    return rows

def get_filter_clause(user: User) -> str:
    """
    Builds a filter clause based on the user's role and permissions.
    """
    filter_clause = {
        "full_permission": "1 = 1",
        "only_from_same_cpf": "cpf = '{user_cpf}'",
        "only_from_same_ap": "'{user_cnes}' IN UNNEST(exibicao.unidades_cadastro)",
        "only_from_same_cnes": "'{user_ap}' IN UNNEST(exibicao.ap_cadastro)",
    }
    return filter_clause[user.access_level].format(
        user_cpf=user.cpf,
        user_ap=user.ap,
        user_cnes=user.cnes,
    )


async def validate_user_access_to_patient_data(user: User, cpf: str) -> tuple[bool, JSONResponse]:
    """
    Validates if a user has access to a patient's data based on their role and permissions.
    Args:
        user (User): The user object containing user details and role permissions.
        cpf (str): The CPF (Cadastro de Pessoas Físicas) number of the patient.
    Returns:
        tuple: A tuple containing a boolean and a JSONResponse.
            - If the user has permission and the data is displayable, returns (True, None).
            - If the patient is not found, returns (False, JSONResponse) with a 404 status code.
            - If the user does not have permission, returns (False, JSONResponse) with a 403
                status code.
            - If the data is not displayable, returns (False, JSONResponse) with a 403 status
                code and reasons for restriction.
    """
    user_permition_filter = get_filter_clause(user)

    # Build the query
    query = f"""
    SELECT
        exibicao.indicador data_is_displayable,
        exibicao.motivos data_display_reasons,
        cast({user_permition_filter} as bool) as user_has_permition
    FROM `{BIGQUERY_PROJECT}`.{BIGQUERY_PATIENT_HEADER_TABLE_ID}
    WHERE
        cpf_particao = {cpf}
    """

    # Execute the query
    results = await read_bq(query, from_file="/tmp/credentials.json")

    if len(results) == 0:
        return False, JSONResponse(
            status_code=404,
            content={
                "message": "Patient not found",
                "type": AccessErrorEnum.NOT_FOUND,
            },
        )
    elif not results[0]["user_has_permition"]:
        return False, JSONResponse(
            status_code=403,
            content={
                "message": "User does not have permission to access this patient",
                "type": AccessErrorEnum.PERMISSION_DENIED,
            },
        )
    elif not results[0]["data_is_displayable"]:
        return False, JSONResponse(
            status_code=403,
            content={
                "message": "Patient is not displayable: "
                + ",".join(results[0]["data_display_reasons"]),
                "type": AccessErrorEnum.DATA_RESTRICTED,
            },
        )
    return True, None


async def request_limiter_identifier(request: Request):
    """
    Generates a unique identifier for rate limiting based on the request's client host and
        endpoint name.
    Args:
        request (Request): The incoming HTTP request object.
    Returns:
        str: A unique identifier in the format "host:endpoint_name".
    Logs:
        - The path and endpoint name of the request.
        - The client host, either from the "X-Forwarded-For" header or directly from the request.
        - The generated unique identifier.
    """
    forwarded = request.headers.get("X-Forwarded-For")

    path = request.scope["path"]
    endpoint_name = path[::-1].split("/", 1)[1][::-1]

    if forwarded:
        host = forwarded.split(',')[0]
    else:
        host = request.client.host

    identifier = host + ":" + endpoint_name
    logger.info(f"Request Limiter :: ID: {identifier}")

    return identifier
