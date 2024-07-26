# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "raw__patientcondition" ADD "is_dirty" BOOL;
        ALTER TABLE "raw__patientrecord" ADD "is_dirty" BOOL;
        ALTER TABLE "std__patientcondition" ADD "is_dirty" BOOL;
        ALTER TABLE "std__patientrecord" ADD "is_dirty" BOOL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "raw__patientrecord" DROP COLUMN "is_dirty";
        ALTER TABLE "raw__patientcondition" DROP COLUMN "is_dirty";
        ALTER TABLE "std__patientrecord" DROP COLUMN "is_dirty";
        ALTER TABLE "std__patientcondition" DROP COLUMN "is_dirty";"""
