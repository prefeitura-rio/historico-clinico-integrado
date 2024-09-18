# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "systemrole" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "type" VARCHAR(13)   DEFAULT 'pipeline_user',
    "slug" VARCHAR(255) NOT NULL UNIQUE,
    "job_title" VARCHAR(255),
    "role_title" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "systemrole"."type" IS 'WEBAPP_USER: frontend_user\nPIPELINE_USER: pipeline_user';
        ALTER TABLE "user" ADD "role_id" INT;
        ALTER TABLE "user" DROP COLUMN "role";
        ALTER TABLE "user" DROP COLUMN "user_class";
        ALTER TABLE "user" ADD CONSTRAINT "fk_user_systemro_775f34a8" FOREIGN KEY ("role_id") REFERENCES "systemrole" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP CONSTRAINT "fk_user_systemro_775f34a8";
        ALTER TABLE "user" ADD "role" VARCHAR(255);
        ALTER TABLE "user" ADD "user_class" VARCHAR(13)   DEFAULT 'pipeline_user';
        ALTER TABLE "user" DROP COLUMN "role_id";
        DROP TABLE IF EXISTS "systemrole";"""
