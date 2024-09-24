# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "city";
        DROP TABLE IF EXISTS "race";
        DROP TABLE IF EXISTS "state";
        DROP TABLE IF EXISTS "gender";
        DROP TABLE IF EXISTS "country";
        DROP TABLE IF EXISTS "occupation";
        DROP TABLE IF EXISTS "nationality";
        DROP TABLE IF EXISTS "raw__encounter";
        DROP TABLE IF EXISTS "conditioncode";
        DROP TABLE IF EXISTS "mrg__patient";
        DROP TABLE IF EXISTS "healthcareteam";
        DROP TABLE IF EXISTS "mrg__patientcns";
        DROP TABLE IF EXISTS "occupationfamily";
        DROP TABLE IF EXISTS "raw__patientrecord";
        DROP TABLE IF EXISTS "healthcareteamtype";
        DROP TABLE IF EXISTS "raw__patientcondition";
        DROP TABLE IF EXISTS "mrg__patientaddress";
        DROP TABLE IF EXISTS "mrg__patienttelecom";
        DROP TABLE IF EXISTS "professionalregistry";
        DROP TABLE IF EXISTS "healthcareprofessional";
        DROP TABLE IF EXISTS "std__patientrecord";
        DROP TABLE IF EXISTS "healthcareprofessional_team";
        DROP TABLE IF EXISTS "std__patientcondition";
        DROP TABLE IF EXISTS "healthcareprofessional_occupation";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ;"""
