# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patient" ALTER COLUMN "race_id" DROP NOT NULL;
        ALTER TABLE "std__patientrecord" ALTER COLUMN "race" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patient" ALTER COLUMN "race_id" SET NOT NULL;
        ALTER TABLE "std__patientrecord" ALTER COLUMN "race" SET NOT NULL;"""
