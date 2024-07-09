# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "datasource" ADD "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "datasource" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "datasource" ALTER COLUMN "system" DROP NOT NULL;
        ALTER TABLE "datasource" ALTER COLUMN "system" TYPE VARCHAR(50) USING "system"::VARCHAR(50);
        ALTER TABLE "datasource" ALTER COLUMN "description" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "datasource" DROP COLUMN "updated_at";
        ALTER TABLE "datasource" DROP COLUMN "created_at";
        ALTER TABLE "datasource" ALTER COLUMN "system" SET NOT NULL;
        ALTER TABLE "datasource" ALTER COLUMN "system" TYPE VARCHAR(10) USING "system"::VARCHAR(10);
        ALTER TABLE "datasource" ALTER COLUMN "description" SET NOT NULL;"""
