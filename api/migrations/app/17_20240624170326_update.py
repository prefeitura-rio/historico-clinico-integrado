from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
CREATE TABLE IF NOT EXISTS "healthcarerolefamily" (
    "code" VARCHAR(4) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "healthcarerole" (
    "cbo" VARCHAR(6) NOT NULL  PRIMARY KEY,
    "description" VARCHAR(512) NOT NULL,
    "family_id" VARCHAR(4) NOT NULL REFERENCES "healthcarerolefamily" ("code") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "healthcareprofessional" (
    "id_sus" VARCHAR(16) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL,
    "cns" VARCHAR(16) NOT NULL,
    "cpf" VARCHAR(11) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "role_id" VARCHAR(6) NOT NULL REFERENCES "healthcarerole" ("cbo") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_healthcarep_cns_b9cb7c" ON "healthcareprofessional" ("cns");
CREATE INDEX IF NOT EXISTS "idx_healthcarep_cpf_3e22a9" ON "healthcareprofessional" ("cpf");
CREATE TABLE IF NOT EXISTS "professionalregistry" (
    "code" VARCHAR(16) NOT NULL  PRIMARY KEY,
    "type" VARCHAR(12) NOT NULL,
    "professional_id" VARCHAR(16) NOT NULL REFERENCES "healthcareprofessional" ("id_sus") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "healthcareprofessional";
        DROP TABLE IF EXISTS "healthcarerole";
        DROP TABLE IF EXISTS "healthcarerolefamily";
        DROP TABLE IF EXISTS "professionalregistry";"""
