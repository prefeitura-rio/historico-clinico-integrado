# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "name" VARCHAR(255);
        ALTER TABLE "user" ADD "cpf" VARCHAR(11)  UNIQUE;
        CREATE UNIQUE INDEX "uid_user_cpf_736ed7" ON "user" ("cpf");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_user_cpf_736ed7";
        ALTER TABLE "user" DROP COLUMN "name";
        ALTER TABLE "user" DROP COLUMN "cpf";"""
