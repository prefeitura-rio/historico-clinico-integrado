# -*- coding: utf-8 -*-
import base64
import io
import secrets
from typing import Optional

import qrcode
from pyotp import TOTP

from app.models import User
from app.auth.types.totp import User2FA as UserPydantic


class TwoFactorAuth:

    def __init__(self, user: UserPydantic, secret_key: str):
        self._user = user
        self._secret_key = secret_key
        self._totp = TOTP(self._secret_key)
        self._qr_cache: Optional[bytes] = None

    @property
    def totp(self) -> TOTP:
        return self._totp

    @property
    def secret_key(self) -> str:
        return self._secret_key

    @staticmethod
    def _generate_secret_key() -> str:
        secret_bytes = secrets.token_bytes(20)
        secret_key = base64.b32encode(secret_bytes).decode("utf-8")
        return secret_key

    @staticmethod
    async def get_or_create_secret_key(user: UserPydantic) -> str:
        user = await User.get_or_none(id=user.id)

        if not user:
            raise ValueError(f"User with id {user.id} not found")

        # If User doesn't have a secret_key, create one
        if not user.secret_key:
            secret_key = TwoFactorAuth._generate_secret_key()
            user.secret_key = secret_key
            await user.save()

        return user.secret_key

    def _create_qr_code(self) -> bytes:
        uri = self.totp.provisioning_uri(
            name=str(self._user.username),
            issuer_name="HCI",
        )
        img = qrcode.make(uri)
        img_byte_array = io.BytesIO()
        img.save(img_byte_array)
        img_byte_array.seek(0)
        return img_byte_array.getvalue()

    @property
    def qr_code(self) -> bytes:
        if self._qr_cache is None:
            self._qr_cache = self._create_qr_code()
        return self._qr_cache

    def verify_totp_code(self, totp_code: str) -> bool:
        return self.totp.verify(totp_code)


async def get_two_factor_auth(
    user: UserPydantic
) -> TwoFactorAuth:
    secret_key = await TwoFactorAuth.get_or_create_secret_key(
        user
    )
    return TwoFactorAuth(user, secret_key)