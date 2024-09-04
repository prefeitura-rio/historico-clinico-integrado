# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import jwt
import hashlib
import json
import os
import base64

from google.cloud import bigquery
from google.oauth2 import service_account
from asyncer import asyncify
from loguru import logger
from passlib.context import CryptContext

from app import config
from app.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_user_token(user: User) -> str:
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
    user = await User.get_or_none(username=username)
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


def merge_versions(current_objs, new_objs: dict) -> None:
    current_fingerprints = {obj.fingerprint: obj for obj in current_objs}
    new_fingerprints = {obj.get("fingerprint"): obj for obj in new_objs}

    to_delete = current_fingerprints.keys() - new_fingerprints.keys()
    to_add = new_fingerprints.keys() - current_fingerprints.keys()

    deletions = [current_fingerprints[fingerprint] for fingerprint in to_delete]
    insertions = [new_fingerprints[fingerprint] for fingerprint in to_add]

    return deletions, insertions


async def update_and_return(instance, new_data):
    await instance.update_from_dict(new_data).save()
    return instance


async def get_instance(Model, table, slug=None, code=None):
    if slug is None:
        return None

    if slug not in table:
        if code:
            table[slug] = await Model.get_or_none(code=code)
        elif slug:
            table[slug] = await Model.get_or_none(slug=slug)

    return table[slug]

def prepare_gcp_credential() -> None:
    base64_credential = os.environ["BASEDOSDADOS_CREDENTIALS_PROD"]

    with open("/tmp/credentials.json", "wb") as f:
        f.write(base64.b64decode(base64_credential))

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"
    return


async def read_bq(query, from_file="/tmp/credentials.json"):
    logger.debug(f"""Reading BigQuery with query (QUERY_PREVIEW_ENABLED={
        os.environ['QUERY_PREVIEW_ENABLED']
    }): {query}""")

    def execute_job():
        credentials = service_account.Credentials.from_service_account_file(
            from_file,
        )
        client = bigquery.Client(credentials=credentials)
        row_iterator = client.query_and_wait(query)
        return [dict(row) for row in row_iterator]

    rows = await asyncify(execute_job)()

    return rows