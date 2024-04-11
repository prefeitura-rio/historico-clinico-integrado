# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE INDEX "idx_std__patien_raw_sou_7a32d6" ON "std__patientcondition" ("raw_source_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_std__patien_raw_sou_7a32d6";"""
