# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "datasource" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "system" VARCHAR(10) NOT NULL,
    "cnes" VARCHAR(50) NOT NULL UNIQUE,
    "description" VARCHAR(512) NOT NULL
);
COMMENT ON COLUMN "datasource"."system" IS 'VITACARE: vitacare\nVITAI: vitai\nPRONTUARIO: prontuario\nSMSRIO: smsrio';
CREATE TABLE IF NOT EXISTS "raw__patientcondition" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "data" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "data_source_id" UUID NOT NULL REFERENCES "datasource" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "raw__patientrecord" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "data" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "data_source_id" UUID NOT NULL REFERENCES "datasource" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "std__patientcondition" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL,
    "cid" VARCHAR(4) NOT NULL,
    "ciap" VARCHAR(4),
    "clinical_status" VARCHAR(32) NOT NULL,
    "category" VARCHAR(32) NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "raw_source_id" UUID NOT NULL REFERENCES "raw__patientcondition" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "std__patientcondition"."clinical_status" IS 'RESOLVED: resolved\nRESOLVING: resolving\nNOT_RESOLVED: not_resolved';
COMMENT ON COLUMN "std__patientcondition"."category" IS 'PROBLEM_LIST_ITEM: problem-list-item\nENCOUTER_DIAGNOSIS: encounter-diagnosis';
CREATE TABLE IF NOT EXISTS "std__patientrecord" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL,
    "birth_city" VARCHAR(32) NOT NULL,
    "birth_state" VARCHAR(32) NOT NULL,
    "birth_country" VARCHAR(32) NOT NULL,
    "birth_date" DATE NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "protected_person" BOOL,
    "deceased" BOOL NOT NULL  DEFAULT False,
    "deceased_date" DATE,
    "father_name" VARCHAR(512),
    "mother_name" VARCHAR(512),
    "name" VARCHAR(512) NOT NULL,
    "naturalization" VARCHAR(32),
    "race" VARCHAR(8) NOT NULL,
    "gender" VARCHAR(7) NOT NULL,
    "nationality" VARCHAR(1) NOT NULL,
    "cns_list" JSONB,
    "addresses_list" JSONB,
    "telecom_list" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "raw_source_id" UUID NOT NULL REFERENCES "raw__patientrecord" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "std__patientrecord"."race" IS 'BRANCA: branca\nPRETA: preta\nPARDA: parda\nAMARELA: amarela\nINDIGENA: indigena';
COMMENT ON COLUMN "std__patientrecord"."gender" IS 'MALE: male\nFEMALE: female\nUNKNOWN: unknown';
COMMENT ON COLUMN "std__patientrecord"."nationality" IS 'BRASILEIRO: B\nESTRANGEIRO: E\nNATURALIZADO: N';
CREATE TABLE IF NOT EXISTS "conditioncode" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "type" VARCHAR(4) NOT NULL,
    "version" VARCHAR(12) NOT NULL,
    "value" VARCHAR(4) NOT NULL
);
COMMENT ON COLUMN "conditioncode"."type" IS 'CID: cid\nCIAP: ciap';
CREATE TABLE IF NOT EXISTS "country" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "code" VARCHAR(10) NOT NULL,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "state" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "code" VARCHAR(10) NOT NULL,
    "name" VARCHAR(512) NOT NULL,
    "country_id" UUID NOT NULL REFERENCES "country" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "city" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "code" VARCHAR(10) NOT NULL,
    "name" VARCHAR(512) NOT NULL,
    "state_id" UUID NOT NULL REFERENCES "state" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "patient" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL UNIQUE,
    "birth_date" DATE NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "protected_person" BOOL,
    "deceased" BOOL NOT NULL  DEFAULT False,
    "deceased_date" DATE,
    "ethnicity" VARCHAR(32) NOT NULL,
    "father_name" VARCHAR(512),
    "mother_name" VARCHAR(512),
    "name" VARCHAR(512) NOT NULL,
    "naturalization" VARCHAR(512),
    "race" VARCHAR(32) NOT NULL,
    "gender" VARCHAR(32) NOT NULL,
    "nationality" VARCHAR(1) NOT NULL,
    "birth_city_id" UUID REFERENCES "city" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "patient"."race" IS 'BRANCA: branca\nPRETA: preta\nPARDA: parda\nAMARELA: amarela\nINDIGENA: indigena';
COMMENT ON COLUMN "patient"."gender" IS 'MALE: male\nFEMALE: female\nUNKNOWN: unknown';
COMMENT ON COLUMN "patient"."nationality" IS 'BRASILEIRO: B\nESTRANGEIRO: E\nNATURALIZADO: N';
CREATE TABLE IF NOT EXISTS "address" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "use" VARCHAR(32) NOT NULL UNIQUE,
    "type" VARCHAR(32) NOT NULL UNIQUE,
    "line" VARCHAR(1024) NOT NULL,
    "postal_code" VARCHAR(8),
    "period_start" DATE,
    "period_end" DATE,
    "city_id" UUID NOT NULL REFERENCES "city" ("id") ON DELETE CASCADE,
    "patient_id" UUID NOT NULL REFERENCES "patient" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "cns" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "value" VARCHAR(16) NOT NULL UNIQUE,
    "is_main" BOOL NOT NULL  DEFAULT False,
    "patient_id" UUID NOT NULL REFERENCES "patient" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "patientcondition" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "clinical_status" VARCHAR(32) NOT NULL,
    "category" VARCHAR(32) NOT NULL,
    "date" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "condition_code_id" UUID NOT NULL REFERENCES "conditioncode" ("id") ON DELETE CASCADE,
    "patient_id" UUID NOT NULL REFERENCES "patient" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "patientcondition"."clinical_status" IS 'RESOLVED: resolved\nRESOLVING: resolving\nNOT_RESOLVED: not_resolved';
COMMENT ON COLUMN "patientcondition"."category" IS 'PROBLEM_LIST_ITEM: problem-list-item\nENCOUTER_DIAGNOSIS: encounter-diagnosis';
CREATE TABLE IF NOT EXISTS "telecom" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "system" VARCHAR(32) NOT NULL UNIQUE,
    "use" VARCHAR(32) NOT NULL UNIQUE,
    "value" VARCHAR(512) NOT NULL,
    "rank" INT,
    "period_start" DATE,
    "period_end" DATE,
    "patient_id" UUID NOT NULL REFERENCES "patient" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "data_source_id" UUID REFERENCES "datasource" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
