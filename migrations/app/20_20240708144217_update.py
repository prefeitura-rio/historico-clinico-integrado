# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
CREATE TABLE IF NOT EXISTS "healthcareteamtype" (
    "code" VARCHAR(4) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "healthcareteam" (
    "ine_code" VARCHAR(10) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL,
    "phone" VARCHAR(16),
    "last_update_professionals" DATE NOT NULL,
    "last_update_team" DATE NOT NULL,
    "healthcare_unit_id" VARCHAR(50) NOT NULL REFERENCES "datasource" ("cnes") ON DELETE CASCADE,
    "team_type_id" VARCHAR(4) NOT NULL REFERENCES "healthcareteamtype" ("code") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "healthcareprofessional_team" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "professional_id" VARCHAR(16) NOT NULL REFERENCES "healthcareprofessional" ("id_sus") ON DELETE CASCADE,
    "team_id" VARCHAR(10) NOT NULL REFERENCES "healthcareteam" ("ine_code") ON DELETE CASCADE,
    CONSTRAINT "uid_healthcarep_profess_b68016" UNIQUE ("professional_id", "team_id")
);
"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "healthcareprofessional_team";
        DROP TABLE IF EXISTS "healthcareteam";
        DROP TABLE IF EXISTS "healthcareteamtype";"""
