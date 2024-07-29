# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patientaddress" ALTER COLUMN "use" DROP NOT NULL;
        ALTER TABLE "patientaddress" ALTER COLUMN "type" DROP NOT NULL;
        ALTER TABLE "patienttelecom" ALTER COLUMN "use" DROP NOT NULL;
        ALTER TABLE "patienttelecom" ALTER COLUMN "system" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patientaddress" ALTER COLUMN "use" SET NOT NULL;
        ALTER TABLE "patientaddress" ALTER COLUMN "type" SET NOT NULL;
        ALTER TABLE "patienttelecom" ALTER COLUMN "use" SET NOT NULL;
        ALTER TABLE "patienttelecom" ALTER COLUMN "system" SET NOT NULL;"""
