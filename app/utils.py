# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import hashlib
import json
import os
import base64
import jwt

from google.cloud import bigquery
from google.oauth2 import service_account
from asyncer import asyncify
from loguru import logger
from fastapi_simple_rate_limiter.database import create_redis_session
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

from app import config
from app.models import User
from app.enums import AccessErrorEnum
from app.config import (
    BIGQUERY_PROJECT,
    BIGQUERY_PATIENT_HEADER_TABLE_ID,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_user_token(user: User) -> str:
    """
    Generates a JWT access token for a given user.
    Args:
        user (User): The user object for which the token is being generated.
    Returns:
        str: The generated JWT access token.
    """

    access_token_expires = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return access_token


async def authenticate_user(username: str, password: str) -> User:
    """Authenticate a user.

    Args:
        username (str): The username of the user to authenticate.
        password (str): The password of the user to authenticate.

    Returns:
        User: The authenticated user.
    """
    user = await User.get_or_none(username=username).prefetch_related("role")
    if not user:
        return None
    if not password_verify(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create an access token.

    Args:
        data (dict): The data to encode into the token.
        expires_delta (timedelta, optional): The expiry time of the token.

    Returns:
        str: The encoded token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


def password_hash(password: str) -> str:
    """Hash a password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def password_verify(password: str, hashed: str) -> bool:
    """Verify a password against a hash.

    Args:
        password (str): The password to verify.
        hashed (str): The hashed password to verify against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return pwd_context.verify(password, hashed)


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

    # Build the filter clause based on the user's role
    user_permition_filter = user.role.permition.filter_clause.format(
        user_cpf=user.cpf,
        user_ap=user.data_source.ap,
        user_cnes=user.data_source,
    )

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


def get_redis_session():
    """
    Establishes a Redis session using the configured host, port, and password.
    Returns:
        redis.Redis: A Redis session object if the host, port, and password are available in envs.
        None: If any of the host, port, or password are missing.
    """

    if REDIS_HOST and REDIS_PORT and REDIS_PASSWORD:
        return create_redis_session(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
    else:
        logger.warning(
            "Could not establish a Redis session because one or more of the required environment variables are missing."  # noqa
        )
        return None
