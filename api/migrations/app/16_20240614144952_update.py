# -*- coding: utf-8 -*-
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "mrg__patient" (
    "patient_code" VARCHAR(20) NOT NULL  PRIMARY KEY,
    "patient_cpf" VARCHAR(11) NOT NULL,
    "birth_date" DATE NOT NULL,
    "active" BOOL NOT NULL  DEFAULT True,
    "protected_person" BOOL,
    "deceased" BOOL NOT NULL  DEFAULT False,
    "deceased_date" DATE,
    "father_name" VARCHAR(512),
    "mother_name" VARCHAR(512),
    "name" VARCHAR(512) NOT NULL,
    "social_name" VARCHAR(512),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "birth_city_id" VARCHAR(10) REFERENCES "city" ("code") ON DELETE CASCADE,
    "gender_id" INT NOT NULL REFERENCES "gender" ("id") ON DELETE CASCADE,
    "nationality_id" INT REFERENCES "nationality" ("id") ON DELETE CASCADE,
    "race_id" INT REFERENCES "race" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "mrg__patientaddress" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "use" VARCHAR(32),
    "type" VARCHAR(32),
    "line" VARCHAR(1024) NOT NULL,
    "postal_code" VARCHAR(8),
    "period_start" DATE,
    "period_end" DATE,
    "fingerprint" VARCHAR(32),
    "city_id" VARCHAR(10) NOT NULL REFERENCES "city" ("code") ON DELETE CASCADE,
    "patient_id" VARCHAR(20) NOT NULL REFERENCES "mrg__patient" ("patient_code") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "mrg__patientcns" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "value" VARCHAR(16) NOT NULL UNIQUE,
    "is_main" BOOL NOT NULL  DEFAULT False,
    "fingerprint" VARCHAR(32),
    "patient_id" VARCHAR(20) NOT NULL REFERENCES "mrg__patient" ("patient_code") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "mrg__patienttelecom" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "system" VARCHAR(32),
    "use" VARCHAR(32),
    "value" VARCHAR(512) NOT NULL,
    "rank" INT,
    "period_start" DATE,
    "period_end" DATE,
    "fingerprint" VARCHAR(32),
    "patient_id" VARCHAR(20) NOT NULL REFERENCES "mrg__patient" ("patient_code") ON DELETE CASCADE
);
        DROP TABLE IF EXISTS "patientcns";
        DROP TABLE IF EXISTS "patientaddress";
        DROP TABLE IF EXISTS "patienttelecom";
        DROP TABLE IF EXISTS "patientcondition";
        DROP TABLE IF EXISTS "patient";
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "mrg__patientaddress";
        DROP TABLE IF EXISTS "mrg__patientcns";
        DROP TABLE IF EXISTS "mrg__patienttelecom";
        DROP TABLE IF EXISTS "mrg__patient";
        """
