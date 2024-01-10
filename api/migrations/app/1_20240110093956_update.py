# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "conditioncode" DROP COLUMN "version";
        ALTER TABLE "patient" DROP COLUMN "ethnicity";
        ALTER TABLE "raw__patientcondition" ADD "patient_cpf" VARCHAR(11) NOT NULL;
        ALTER TABLE "raw__patientrecord" ADD "patient_cpf" VARCHAR(11) NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patient" ADD "ethnicity" VARCHAR(32) NOT NULL;
        ALTER TABLE "conditioncode" ADD "version" VARCHAR(12) NOT NULL;
        ALTER TABLE "raw__patientrecord" DROP COLUMN "patient_cpf";
        ALTER TABLE "raw__patientcondition" DROP COLUMN "patient_cpf";"""
