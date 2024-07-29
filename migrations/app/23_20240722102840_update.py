# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "datasource" ALTER COLUMN "system" TYPE VARCHAR(50) USING "system"::VARCHAR(50);
        ALTER TABLE "raw__encounter" ALTER COLUMN "source_id" TYPE VARCHAR(100) USING "source_id"::VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "datasource" ALTER COLUMN "system" TYPE VARCHAR(50) USING "system"::VARCHAR(50);
        ALTER TABLE "raw__encounter" ALTER COLUMN "source_id" TYPE TIMESTAMPTZ USING "source_id"::TIMESTAMPTZ;"""
