# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "std__patientrecord" RENAME COLUMN "addresses_list" TO "address_list";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "std__patientrecord" RENAME COLUMN "address_list" TO "addresses_list";"""
