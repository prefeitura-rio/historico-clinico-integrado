# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "datasource" ADD "ap" VARCHAR(2);
        CREATE TABLE IF NOT EXISTS "permition" (
            "slug" VARCHAR(19) NOT NULL  PRIMARY KEY DEFAULT 'only_from_same_cpf',
            "description" VARCHAR(255) NOT NULL,
            "filter_clause" VARCHAR(255) NOT NULL,
            "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
        );
        COMMENT ON COLUMN "permition"."slug" IS 'PIPELINE_READ: pipeline_read\nPIPELINE_WRITE: pipeline_write\nPIPELINE_READWRITE: pipeline_readwrite\nHCI_SAME_CPF: only_from_same_cpf\nHCI_SAME_HEALTHUNIT: only_from_same_unit\nHCI_SAME_AP: only_from_same_ap\nHCI_FULL_PERMITION: full_permition';
        CREATE TABLE IF NOT EXISTS "systemrole" (
            "slug" VARCHAR(255) NOT NULL  PRIMARY KEY,
            "job_title" VARCHAR(255),
            "role_title" VARCHAR(255),
            "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            "permition_id" VARCHAR(19) REFERENCES "permition" ("slug") ON DELETE CASCADE
        );
        ALTER TABLE "user" RENAME COLUMN "role" TO "role_id";
        ALTER TABLE "user" DROP COLUMN "user_class";
        ALTER TABLE "user" ADD CONSTRAINT "fk_user_systemro_cd2eaaa6" FOREIGN KEY ("role_id") REFERENCES "systemrole" ("slug") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP CONSTRAINT "fk_user_systemro_cd2eaaa6";
        ALTER TABLE "user" RENAME COLUMN "role_id" TO "role";
        ALTER TABLE "user" ADD "user_class" VARCHAR(13)   DEFAULT 'pipeline_user';
        ALTER TABLE "datasource" DROP COLUMN "ap";
        DROP TABLE IF EXISTS "permition";
        DROP TABLE IF EXISTS "systemrole";"""
