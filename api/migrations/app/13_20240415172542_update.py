# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE INDEX "idx_raw__patien_created_258f98" ON "raw__patientcondition" ("created_at");
        CREATE INDEX "idx_raw__patien_updated_bb2269" ON "raw__patientcondition" ("updated_at");
        CREATE INDEX "idx_raw__patien_created_9478df" ON "raw__patientrecord" ("created_at");
        CREATE INDEX "idx_raw__patien_updated_2e522a" ON "raw__patientrecord" ("updated_at");
        CREATE INDEX "idx_std__patien_created_401030" ON "std__patientcondition" ("created_at");
        CREATE INDEX "idx_std__patien_updated_b6a86e" ON "std__patientcondition" ("updated_at");
        CREATE INDEX "idx_std__patien_updated_c98131" ON "std__patientrecord" ("updated_at");
        CREATE INDEX "idx_std__patien_created_8156aa" ON "std__patientrecord" ("created_at");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_std__patien_updated_b6a86e";
        DROP INDEX "idx_std__patien_created_401030";
        DROP INDEX "idx_std__patien_created_8156aa";
        DROP INDEX "idx_std__patien_updated_c98131";
        DROP INDEX "idx_raw__patien_updated_bb2269";
        DROP INDEX "idx_raw__patien_created_258f98";
        DROP INDEX "idx_raw__patien_updated_2e522a";
        DROP INDEX "idx_raw__patien_created_9478df";"""
