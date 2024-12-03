# -*- coding: utf-8 -*-
from loguru import logger
import requests
import redis
import secrets

from app.models import User
from app.config import (
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    DATARELAY_URL,
    DATARELAY_MAILMAN_TOKEN,
    EMAIL_BODY_2FA,
    EMAIL_SUBJECT_2FA,
)


redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=0
)


def store_code(user: User, code: str, ttl: int = 300):
    redis_client.setex(f"2fa:{user.id}", ttl, code)


async def validate_code(user: User, code: str):
    stored_code = redis_client.get(f"2fa:{user.id}")

    if store_code is None:
        return False

    if stored_code.decode() == code:
        redis_client.delete(f"2fa:{user.id}")
        return True

    return False


def generate_2fa_code():
    return f"{secrets.randbelow(1000000):06}"


async def send_2fa_email_to_user(user: User, code: str):
    logger.info(f"Sending 2FA code {code} to {user.email}")
    response = requests.post(
        url=DATARELAY_URL,
        headers={
            'x-api-key': DATARELAY_MAILMAN_TOKEN
        },
        body={
            "to_addresses": [user.email],
            "cc_addresses": [],
            "bcc_addresses": [],
            "subject": EMAIL_SUBJECT_2FA,
            "body": EMAIL_BODY_2FA.format(code=code),
            "is_html_body": True
        }
    )
    if response.status_code == 200:
        return True
    else:
        return False



