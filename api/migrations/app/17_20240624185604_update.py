# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
CREATE TABLE IF NOT EXISTS "occupationfamily" (
    "code" VARCHAR(4) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "occupation" (
    "cbo" VARCHAR(6) NOT NULL  PRIMARY KEY,
    "description" VARCHAR(512) NOT NULL,
    "family_id" VARCHAR(4) NOT NULL REFERENCES "occupationfamily" ("code") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "healthcareprofessional" (
    "id_sus" VARCHAR(16) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL,
    "cns" VARCHAR(16) NOT NULL,
    "cpf" VARCHAR(11),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_healthcarep_cns_b9cb7c" ON "healthcareprofessional" ("cns");
CREATE INDEX IF NOT EXISTS "idx_healthcarep_cpf_3e22a9" ON "healthcareprofessional" ("cpf");
        CREATE TABLE IF NOT EXISTS "healthcareprofessional_occupation" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "professional_id" VARCHAR(16) NOT NULL REFERENCES "healthcareprofessional" ("id_sus") ON DELETE CASCADE,
    "role_id" VARCHAR(6) NOT NULL REFERENCES "occupation" ("cbo") ON DELETE CASCADE,
    CONSTRAINT "uid_healthcarep_profess_18ff4d" UNIQUE ("professional_id", "role_id")
);
CREATE TABLE IF NOT EXISTS "professionalregistry" (
    "code" VARCHAR(16) NOT NULL  PRIMARY KEY,
    "type" VARCHAR(12) NOT NULL,
    "professional_id" VARCHAR(16) NOT NULL REFERENCES "healthcareprofessional" ("id_sus") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "healthcareprofessional";
        DROP TABLE IF EXISTS "healthcareprofessional_occupation";
        DROP TABLE IF EXISTS "occupation";
        DROP TABLE IF EXISTS "occupationfamily";
        DROP TABLE IF EXISTS "professionalregistry";"""
