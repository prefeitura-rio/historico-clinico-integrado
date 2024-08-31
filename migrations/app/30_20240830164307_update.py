# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" RENAME COLUMN "is_2fa_enabled" TO "is_2fa_required";
        ALTER TABLE "user" RENAME COLUMN "is_2fa_active" TO "is_2fa_activated";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" RENAME COLUMN "is_2fa_required" TO "is_2fa_active";
        ALTER TABLE "user" RENAME COLUMN "is_2fa_activated" TO "is_2fa_active";
        ALTER TABLE "user" RENAME COLUMN "is_2fa_required" TO "is_2fa_enabled";
        ALTER TABLE "user" RENAME COLUMN "is_2fa_activated" TO "is_2fa_enabled";"""
