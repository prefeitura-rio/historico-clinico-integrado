# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import hashlib
import json
import jwt
import basedosdados as bd

from passlib.context import CryptContext
from loguru import logger

from app import config
from app.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def upload_to_datalake(
    input_path: str,
    dataset_id: str,
    table_id: str,
    dump_mode: str = "append",
    source_format: str = "csv",
    csv_delimiter: str = ";",
    if_exists: str = "replace",
    if_storage_data_exists: str = "replace",
    biglake_table: bool = True,
    dataset_is_public: bool = False,
):
    """
    Uploads data to a Google Cloud Storage bucket and creates or appends to a BigQuery table.

    Args:
        input_path (str): The path to the input data file.
        dataset_id (str): The ID of the BigQuery dataset.
        table_id (str): The ID of the BigQuery table.
        dump_mode (str, optional): The dump mode for the table. Defaults to "append". Accepted values are "append" and "overwrite".
        source_format (str, optional): The format of the input data. Defaults to "csv". Accepted values are "csv" and "parquet".
        csv_delimiter (str, optional): The delimiter used in the CSV file. Defaults to ";".
        if_exists (str, optional): The behavior if the table already exists. Defaults to "replace".
        if_storage_data_exists (str, optional): The behavior if the storage data already exists. Defaults to "replace".
        biglake_table (bool, optional): Whether the table is a BigLake table. Defaults to True.
        dataset_is_public (bool, optional): Whether the dataset is public. Defaults to False.

    Raises:
        RuntimeError: If an error occurs during the upload process.

    Returns:
        None
    """
    if input_path == "":
        logger.warning("Received input_path=''. No data to upload")
        return

    tb = bd.Table(dataset_id=dataset_id, table_id=table_id)
    table_staging = f"{tb.table_full_name['staging']}"
    st = bd.Storage(dataset_id=dataset_id, table_id=table_id)
    storage_path = f"{st.bucket_name}.staging.{dataset_id}.{table_id}"
    storage_path_link = (
        f"https://console.cloud.google.com/storage/browser/{st.bucket_name}"
        f"/staging/{dataset_id}/{table_id}"
    )
    logger.info(f"Uploading file {input_path} to {storage_path} with {source_format} format")

    try:
        table_exists = tb.table_exists(mode="staging")

        if not table_exists:
            logger.info(f"CREATING TABLE: {dataset_id}.{table_id}")
            tb.create(
                path=input_path,
                source_format=source_format,
                csv_delimiter=csv_delimiter,
                if_storage_data_exists=if_storage_data_exists,
                biglake_table=biglake_table,
                dataset_is_public=dataset_is_public,
            )
        else:
            if dump_mode == "append":
                logger.info(
                    f"TABLE ALREADY EXISTS APPENDING DATA TO STORAGE: {dataset_id}.{table_id}"
                )

                tb.append(filepath=input_path, if_exists=if_exists)
            elif dump_mode == "overwrite":
                logger.info(
                    "MODE OVERWRITE: Table ALREADY EXISTS, DELETING OLD DATA!\n"
                    f"{storage_path}\n"
                    f"{storage_path_link}"
                )  # pylint: disable=C0301
                st.delete_table(mode="staging", bucket_name=st.bucket_name, not_found_ok=True)
                logger.info(
                    "MODE OVERWRITE: Sucessfully DELETED OLD DATA from Storage:\n"
                    f"{storage_path}\n"
                    f"{storage_path_link}"
                )  # pylint: disable=C0301
                tb.delete(mode="all")
                logger.info(
                    "MODE OVERWRITE: Sucessfully DELETED TABLE:\n" f"{table_staging}\n"
                )  # pylint: disable=C0301

                tb.create(
                    path=input_path,
                    source_format=source_format,
                    csv_delimiter=csv_delimiter,
                    if_storage_data_exists=if_storage_data_exists,
                    biglake_table=biglake_table,
                    dataset_is_public=dataset_is_public,
                )
        logger.info("Data uploaded to BigQuery")

    except Exception as e:  # pylint: disable=W0703
        logger.error(f"An error occurred: {e}", level="error")
        raise RuntimeError() from e
