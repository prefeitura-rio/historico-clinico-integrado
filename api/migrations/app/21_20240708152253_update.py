# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "healthcareprofessional_team" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "healthcareteam" ADD "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "healthcareteam" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "healthcareteam" DROP COLUMN "last_update_professionals";
        ALTER TABLE "healthcareteam" DROP COLUMN "last_update_team";
        ALTER TABLE "healthcareteamtype" ADD "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "healthcareteamtype" ADD "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "healthcareteam" ADD "last_update_professionals" DATE NOT NULL;
        ALTER TABLE "healthcareteam" ADD "last_update_team" DATE NOT NULL;
        ALTER TABLE "healthcareteam" DROP COLUMN "updated_at";
        ALTER TABLE "healthcareteam" DROP COLUMN "created_at";
        ALTER TABLE "healthcareteamtype" DROP COLUMN "updated_at";
        ALTER TABLE "healthcareteamtype" DROP COLUMN "created_at";
        ALTER TABLE "healthcareprofessional_team" DROP COLUMN "created_at";"""
