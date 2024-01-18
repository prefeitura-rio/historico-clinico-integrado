# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patientcondition" ALTER COLUMN "category" DROP NOT NULL;
        ALTER TABLE "patientcondition" ALTER COLUMN "category" TYPE VARCHAR(19) USING "category"::VARCHAR(19);
        ALTER TABLE "patientcondition" ALTER COLUMN "clinical_status" DROP NOT NULL;
        ALTER TABLE "patientcondition" ALTER COLUMN "clinical_status" TYPE VARCHAR(12) USING "clinical_status"::VARCHAR(12);
        ALTER TABLE "std__patientcondition" ALTER COLUMN "category" DROP NOT NULL;
        ALTER TABLE "std__patientcondition" ALTER COLUMN "category" TYPE VARCHAR(19) USING "category"::VARCHAR(19);
        ALTER TABLE "std__patientcondition" ALTER COLUMN "clinical_status" DROP NOT NULL;
        ALTER TABLE "std__patientcondition" ALTER COLUMN "clinical_status" TYPE VARCHAR(12) USING "clinical_status"::VARCHAR(12);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "patientcondition" ALTER COLUMN "category" SET NOT NULL;
        ALTER TABLE "patientcondition" ALTER COLUMN "category" TYPE VARCHAR(32) USING "category"::VARCHAR(32);
        ALTER TABLE "patientcondition" ALTER COLUMN "clinical_status" SET NOT NULL;
        ALTER TABLE "patientcondition" ALTER COLUMN "clinical_status" TYPE VARCHAR(32) USING "clinical_status"::VARCHAR(32);
        ALTER TABLE "std__patientcondition" ALTER COLUMN "category" SET NOT NULL;
        ALTER TABLE "std__patientcondition" ALTER COLUMN "category" TYPE VARCHAR(32) USING "category"::VARCHAR(32);
        ALTER TABLE "std__patientcondition" ALTER COLUMN "clinical_status" SET NOT NULL;
        ALTER TABLE "std__patientcondition" ALTER COLUMN "clinical_status" TYPE VARCHAR(32) USING "clinical_status"::VARCHAR(32);"""
