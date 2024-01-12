# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patient" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "patientcondition" DROP COLUMN "updated_at";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patient" DROP COLUMN "created_at";
        ALTER TABLE "patientcondition" ADD "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;"""
