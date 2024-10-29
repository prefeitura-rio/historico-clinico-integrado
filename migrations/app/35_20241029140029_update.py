# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "use_terms_accepted_at" TIMESTAMPTZ;
        ALTER TABLE "user" ADD "is_use_terms_accepted" BOOL NOT NULL  DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "use_terms_accepted_at";
        ALTER TABLE "user" DROP COLUMN "is_use_terms_accepted";"""
