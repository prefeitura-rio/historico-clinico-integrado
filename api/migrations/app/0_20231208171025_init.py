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
CREATE TABLE IF NOT EXISTS "addresstype" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(32) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "addressuse" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(32) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "country" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "datasource" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "ethnicity" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(32) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "gender" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(32) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "nationality" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(32) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "patient" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "cpf" VARCHAR(11) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "race" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(32) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "rawpatientrecord" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "data" JSONB NOT NULL,
    "data_source_id" UUID NOT NULL REFERENCES "datasource" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "state" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL,
    "country_id" UUID NOT NULL REFERENCES "country" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "city" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(512) NOT NULL,
    "state_id" UUID NOT NULL REFERENCES "state" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "address" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "line" VARCHAR(1024) NOT NULL,
    "postal_code" VARCHAR(8),
    "city_id" UUID NOT NULL REFERENCES "city" ("id") ON DELETE CASCADE,
    "type_id" UUID REFERENCES "addresstype" ("id") ON DELETE CASCADE,
    "use_id" UUID REFERENCES "addressuse" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "patientrecord" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "active" BOOL NOT NULL  DEFAULT True,
    "birth_date" DATE NOT NULL,
    "deceased" BOOL NOT NULL  DEFAULT False,
    "deceased_date" DATE,
    "father_name" VARCHAR(512),
    "mother_name" VARCHAR(512),
    "name" VARCHAR(512) NOT NULL,
    "naturalization" VARCHAR(512),
    "protected_person" BOOL,
    "birth_city_id" UUID REFERENCES "city" ("id") ON DELETE CASCADE,
    "data_source_id" UUID NOT NULL REFERENCES "datasource" ("id") ON DELETE CASCADE,
    "ethnicity_id" UUID REFERENCES "ethnicity" ("id") ON DELETE CASCADE,
    "gender_id" UUID REFERENCES "gender" ("id") ON DELETE CASCADE,
    "nationality_id" UUID REFERENCES "nationality" ("id") ON DELETE CASCADE,
    "patient_id" UUID NOT NULL REFERENCES "patient" ("id") ON DELETE CASCADE,
    "race_id" UUID REFERENCES "race" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_patientreco_patient_bb8755" UNIQUE ("patient_id", "data_source_id")
);
CREATE TABLE IF NOT EXISTS "addresspatientperiod" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "period_start" DATE,
    "period_end" DATE,
    "address_id" UUID NOT NULL REFERENCES "address" ("id") ON DELETE CASCADE,
    "patient_id" INT NOT NULL REFERENCES "patientrecord" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "cns" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "value" VARCHAR(16) NOT NULL UNIQUE,
    "is_main" BOOL NOT NULL  DEFAULT False,
    "patient_id" INT NOT NULL REFERENCES "patientrecord" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "telecomsystem" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(32) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "telecomuse" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "slug" VARCHAR(32) NOT NULL UNIQUE,
    "name" VARCHAR(512) NOT NULL
);
CREATE TABLE IF NOT EXISTS "telecom" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "value" VARCHAR(512) NOT NULL,
    "rank" INT,
    "system_id" UUID REFERENCES "telecomsystem" ("id") ON DELETE CASCADE,
    "use_id" UUID REFERENCES "telecomuse" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "telecompatientperiod" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "period_start" DATE,
    "period_end" DATE,
    "patient_id" INT NOT NULL REFERENCES "patientrecord" ("id") ON DELETE CASCADE,
    "telecom_id" UUID NOT NULL REFERENCES "telecom" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
