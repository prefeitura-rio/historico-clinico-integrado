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
CREATE TABLE IF NOT EXISTS "conditioncode" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "type" VARCHAR(4) NOT NULL,
    "value" VARCHAR(5) NOT NULL,
    "description" VARCHAR(512) NOT NULL
);
COMMENT ON COLUMN "conditioncode"."type" IS 'CID: cid\nCIAP: ciap';
CREATE TABLE IF NOT EXISTS "country" (
    "code" VARCHAR(10) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "datasource" (
    "cnes" VARCHAR(50) NOT NULL  PRIMARY KEY,
    "system" VARCHAR(10) NOT NULL,
    "description" VARCHAR(512) NOT NULL
);
COMMENT ON COLUMN "datasource"."system" IS 'VITACARE: vitacare\nVITAI: vitai\nPRONTUARIO: prontuario\nSMSRIO: smsrio';
CREATE TABLE IF NOT EXISTS "gender" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(7) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
COMMENT ON COLUMN "gender"."slug" IS 'MALE: male\nFEMALE: female\nUNKNOWN: unknown';
CREATE TABLE IF NOT EXISTS "nationality" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(1) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
COMMENT ON COLUMN "nationality"."slug" IS 'BRASILEIRO: B\nESTRANGEIRO: E\nNATURALIZADO: N';
CREATE TABLE IF NOT EXISTS "race" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(8) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
COMMENT ON COLUMN "race"."slug" IS 'BRANCA: branca\nPRETA: preta\nPARDA: parda\nAMARELA: amarela\nINDIGENA: indigena';
CREATE TABLE IF NOT EXISTS "raw__patientcondition" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL,
    "data" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "data_source_id" VARCHAR(50) NOT NULL REFERENCES "datasource" ("cnes") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "raw__patientrecord" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL,
    "data" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "data_source_id" VARCHAR(50) NOT NULL REFERENCES "datasource" ("cnes") ON DELETE CASCADE
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
CREATE TABLE IF NOT EXISTS "state" (
    "code" VARCHAR(10) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL,
    "country_id" VARCHAR(10) NOT NULL REFERENCES "country" ("code") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "city" (
    "code" VARCHAR(10) NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL,
    "state_id" VARCHAR(10) NOT NULL REFERENCES "state" ("code") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "patient" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL UNIQUE,
    "birth_date" DATE NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "protected_person" BOOL,
    "deceased" BOOL NOT NULL  DEFAULT False,
    "deceased_date" DATE,
    "father_name" VARCHAR(512),
    "mother_name" VARCHAR(512),
    "name" VARCHAR(512) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "birth_city_id" VARCHAR(10) REFERENCES "city" ("code") ON DELETE CASCADE,
    "gender_id" UUID NOT NULL REFERENCES "gender" ("id") ON DELETE CASCADE,
    "nationality_id" UUID NOT NULL REFERENCES "nationality" ("id") ON DELETE CASCADE,
    "race_id" UUID NOT NULL REFERENCES "race" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "patientaddress" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "use" VARCHAR(32) NOT NULL,
    "type" VARCHAR(32) NOT NULL,
    "line" VARCHAR(1024) NOT NULL,
    "postal_code" VARCHAR(8),
    "period_start" DATE,
    "period_end" DATE,
    "city_id" VARCHAR(10) NOT NULL REFERENCES "city" ("code") ON DELETE CASCADE,
    "patient_id" UUID NOT NULL REFERENCES "patient" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "patientcns" (
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
CREATE TABLE IF NOT EXISTS "patienttelecom" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "system" VARCHAR(32) NOT NULL,
    "use" VARCHAR(32) NOT NULL,
    "value" VARCHAR(512) NOT NULL,
    "rank" INT,
    "period_start" DATE,
    "period_end" DATE,
    "patient_id" UUID NOT NULL REFERENCES "patient" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "std__patientrecord" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL,
    "birth_date" DATE NOT NULL,
    "active" BOOL   DEFAULT True,
    "protected_person" BOOL,
    "deceased" BOOL   DEFAULT False,
    "deceased_date" DATE,
    "father_name" VARCHAR(512),
    "mother_name" VARCHAR(512),
    "name" VARCHAR(512) NOT NULL,
    "race" VARCHAR(8) NOT NULL,
    "gender" VARCHAR(7) NOT NULL,
    "nationality" VARCHAR(1) NOT NULL,
    "cns_list" JSONB,
    "address_list" JSONB,
    "telecom_list" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "birth_city_id" VARCHAR(10) REFERENCES "city" ("code") ON DELETE CASCADE,
    "birth_country_id" VARCHAR(10) REFERENCES "country" ("code") ON DELETE CASCADE,
    "birth_state_id" VARCHAR(10) REFERENCES "state" ("code") ON DELETE CASCADE,
    "raw_source_id" UUID NOT NULL REFERENCES "raw__patientrecord" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "std__patientrecord"."race" IS 'BRANCA: branca\nPRETA: preta\nPARDA: parda\nAMARELA: amarela\nINDIGENA: indigena';
COMMENT ON COLUMN "std__patientrecord"."gender" IS 'MALE: male\nFEMALE: female\nUNKNOWN: unknown';
COMMENT ON COLUMN "std__patientrecord"."nationality" IS 'BRASILEIRO: B\nESTRANGEIRO: E\nNATURALIZADO: N';
CREATE TABLE IF NOT EXISTS "user" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "data_source_id" VARCHAR(50) REFERENCES "datasource" ("cnes") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
