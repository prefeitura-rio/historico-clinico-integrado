# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "raw__encounter" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL,
    "patient_code" VARCHAR(20) NOT NULL,
    "data" JSONB NOT NULL,
    "source_updated_at" TIMESTAMPTZ NOT NULL,
    "source_id" TIMESTAMPTZ NOT NULL,
    "is_valid" BOOL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "creator_id" INT REFERENCES "user" ("id") ON DELETE CASCADE,
    "data_source_id" VARCHAR(50) NOT NULL REFERENCES "datasource" ("cnes") ON DELETE CASCADE,
    CONSTRAINT "uid_raw__encoun_patient_837195" UNIQUE ("patient_code", "data_source_id", "source_id")
);
CREATE INDEX IF NOT EXISTS "idx_raw__encoun_patient_898253" ON "raw__encounter" ("patient_cpf");
CREATE INDEX IF NOT EXISTS "idx_raw__encoun_patient_697b4b" ON "raw__encounter" ("patient_code");
CREATE INDEX IF NOT EXISTS "idx_raw__encoun_created_7d4b24" ON "raw__encounter" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_raw__encoun_updated_78d6d9" ON "raw__encounter" ("updated_at");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "raw__encounter";"""
