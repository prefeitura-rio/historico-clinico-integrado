# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "userhistory" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "method" VARCHAR(10) NOT NULL,
    "path" VARCHAR(100) NOT NULL,
    "query_params" JSONB,
    "body" JSONB,
    "status_code" INT NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "userhistory";"""
