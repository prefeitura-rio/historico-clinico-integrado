from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP CONSTRAINT "fk_user_datasour_4e42e1df";
        ALTER TABLE "user" DROP CONSTRAINT "fk_user_systemro_cd2eaaa6";
        ALTER TABLE "user" ADD "ap" VARCHAR(2);
        ALTER TABLE "user" ADD "access_level" VARCHAR(50);
        ALTER TABLE "user" ADD "job_title" VARCHAR(255);
        ALTER TABLE "user" RENAME COLUMN "data_source_id" TO "cnes";
        ALTER TABLE "user" DROP COLUMN "password";
        ALTER TABLE "user" DROP COLUMN "is_2fa_required";
        ALTER TABLE "user" DROP COLUMN "is_ergon_validation_required";
        ALTER TABLE "user" DROP COLUMN "role_id";
        ALTER TABLE "user" DROP COLUMN "is_2fa_activated";
        ALTER TABLE "user" DROP COLUMN "secret_key";
        DROP TABLE IF EXISTS "permition";
        DROP TABLE IF EXISTS "datasource";
        DROP TABLE IF EXISTS "systemrole";
        DROP TABLE IF EXISTS "meta__tableinitialization";
        CREATE INDEX "idx_user_access__8a819a" ON "user" ("access_level");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_user_access__8a819a";
        ALTER TABLE "user" ADD "password" VARCHAR(255) NOT NULL;
        ALTER TABLE "user" ADD "is_2fa_required" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "user" RENAME COLUMN "cnes" TO "data_source_id";
        ALTER TABLE "user" ADD "is_ergon_validation_required" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "user" ADD "role_id" VARCHAR(255);
        ALTER TABLE "user" ADD "is_2fa_activated" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "user" ADD "secret_key" VARCHAR(255);
        ALTER TABLE "user" DROP COLUMN "ap";
        ALTER TABLE "user" DROP COLUMN "access_level";
        ALTER TABLE "user" DROP COLUMN "job_title";
        ALTER TABLE "user" ADD CONSTRAINT "fk_user_systemro_cd2eaaa6" FOREIGN KEY ("role_id") REFERENCES "systemrole" ("slug") ON DELETE CASCADE;
        ALTER TABLE "user" ADD CONSTRAINT "fk_user_datasour_4e42e1df" FOREIGN KEY ("data_source_id") REFERENCES "datasource" ("cnes") ON DELETE CASCADE;"""
