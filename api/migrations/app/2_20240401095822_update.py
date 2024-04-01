# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "raw__patientcondition" RENAME COLUMN "is_dirty" TO "is_valid";
        ALTER TABLE "raw__patientrecord" RENAME COLUMN "is_dirty" TO "is_valid";
        ALTER TABLE "std__patientcondition" RENAME COLUMN "is_dirty" TO "is_valid";
        ALTER TABLE "std__patientrecord" RENAME COLUMN "is_dirty" TO "is_valid";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "raw__patientrecord" RENAME COLUMN "is_valid" TO "is_dirty";
        ALTER TABLE "raw__patientcondition" RENAME COLUMN "is_valid" TO "is_dirty";
        ALTER TABLE "std__patientrecord" RENAME COLUMN "is_valid" TO "is_dirty";
        ALTER TABLE "std__patientcondition" RENAME COLUMN "is_valid" TO "is_dirty";"""
