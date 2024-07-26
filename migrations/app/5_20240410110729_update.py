# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "raw__patientrecord" DROP CONSTRAINT "fk_raw__pat_user_f8125948";
        ALTER TABLE "raw__patientcondition" DROP CONSTRAINT "fk_raw__pat_user_020aedef";
        ALTER TABLE "raw__patientcondition" RENAME COLUMN "created_by_id" TO "creator_id";
        ALTER TABLE "raw__patientrecord" RENAME COLUMN "created_by_id" TO "creator_id";
        ALTER TABLE "raw__patientcondition" ADD CONSTRAINT "fk_raw__pat_user_e7969274" FOREIGN KEY ("creator_id") REFERENCES "user" ("id") ON DELETE CASCADE;
        ALTER TABLE "raw__patientrecord" ADD CONSTRAINT "fk_raw__pat_user_af1bbb64" FOREIGN KEY ("creator_id") REFERENCES "user" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "raw__patientcondition" DROP CONSTRAINT "fk_raw__pat_user_e7969274";
        ALTER TABLE "raw__patientrecord" DROP CONSTRAINT "fk_raw__pat_user_af1bbb64";
        ALTER TABLE "raw__patientrecord" RENAME COLUMN "creator_id" TO "created_by_id";
        ALTER TABLE "raw__patientcondition" RENAME COLUMN "creator_id" TO "created_by_id";
        ALTER TABLE "raw__patientrecord" ADD CONSTRAINT "fk_raw__pat_user_f8125948" FOREIGN KEY ("created_by_id") REFERENCES "user" ("id") ON DELETE CASCADE;
        ALTER TABLE "raw__patientcondition" ADD CONSTRAINT "fk_raw__pat_user_020aedef" FOREIGN KEY ("created_by_id") REFERENCES "user" ("id") ON DELETE CASCADE;"""
