# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patient" ADD "patient_code" VARCHAR(20) NOT NULL UNIQUE;
        ALTER TABLE "raw__patientcondition" ADD "patient_code" VARCHAR(20) NOT NULL;
        ALTER TABLE "raw__patientrecord" ADD "patient_code" VARCHAR(20) NOT NULL;
        ALTER TABLE "std__patientcondition" ADD "patient_code" VARCHAR(20) NOT NULL;
        ALTER TABLE "std__patientrecord" ADD "patient_code" VARCHAR(20) NOT NULL;
        CREATE UNIQUE INDEX "uid_patient_patient_5bd71b" ON "patient" ("patient_code");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_patient_patient_5bd71b";
        ALTER TABLE "patient" DROP COLUMN "patient_code";
        ALTER TABLE "raw__patientrecord" DROP COLUMN "patient_code";
        ALTER TABLE "raw__patientcondition" DROP COLUMN "patient_code";
        ALTER TABLE "std__patientrecord" DROP COLUMN "patient_code";
        ALTER TABLE "std__patientcondition" DROP COLUMN "patient_code";"""
