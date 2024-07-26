# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patientaddress" ADD "fingerprint" VARCHAR(32);
        ALTER TABLE "patientcns" ADD "fingerprint" VARCHAR(32);
        ALTER TABLE "patienttelecom" ADD "fingerprint" VARCHAR(32);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patientcns" DROP COLUMN "fingerprint";
        ALTER TABLE "patientaddress" DROP COLUMN "fingerprint";
        ALTER TABLE "patienttelecom" DROP COLUMN "fingerprint";"""
