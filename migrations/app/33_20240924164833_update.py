# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "city" CASCADE;
        DROP TABLE IF EXISTS "race" CASCADE;
        DROP TABLE IF EXISTS "state" CASCADE;
        DROP TABLE IF EXISTS "gender" CASCADE;
        DROP TABLE IF EXISTS "country" CASCADE;
        DROP TABLE IF EXISTS "occupation" CASCADE;
        DROP TABLE IF EXISTS "nationality" CASCADE;
        DROP TABLE IF EXISTS "raw__encounter" CASCADE;
        DROP TABLE IF EXISTS "conditioncode" CASCADE;
        DROP TABLE IF EXISTS "mrg__patient" CASCADE;
        DROP TABLE IF EXISTS "healthcareteam" CASCADE;
        DROP TABLE IF EXISTS "mrg__patientcns" CASCADE;
        DROP TABLE IF EXISTS "occupationfamily" CASCADE;
        DROP TABLE IF EXISTS "raw__patientrecord" CASCADE;
        DROP TABLE IF EXISTS "healthcareteamtype" CASCADE;
        DROP TABLE IF EXISTS "raw__patientcondition" CASCADE;
        DROP TABLE IF EXISTS "mrg__patientaddress" CASCADE;
        DROP TABLE IF EXISTS "mrg__patienttelecom" CASCADE;
        DROP TABLE IF EXISTS "professionalregistry" CASCADE;
        DROP TABLE IF EXISTS "healthcareprofessional" CASCADE;
        DROP TABLE IF EXISTS "std__patientrecord" CASCADE;
        DROP TABLE IF EXISTS "healthcareprofessional_team" CASCADE;
        DROP TABLE IF EXISTS "std__patientcondition" CASCADE;
        DROP TABLE IF EXISTS "healthcareprofessional_occupation" CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ;"""
