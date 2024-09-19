from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "permition" (
    "slug" VARCHAR(19) NOT NULL  PRIMARY KEY DEFAULT 'only_from_same_cpf',
    "description" VARCHAR(255) NOT NULL,
    "filter_clause" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "permition"."slug" IS 'PIPELINE_READ: pipeline_read\nPIPELINE_WRITE: pipeline_write\nPIPELINE_READWRITE: pipeline_readwrite\nHCI_SAME_CPF: only_from_same_cpf\nHCI_SAME_HEALTHUNIT: only_from_same_unit\nHCI_SAME_AP: only_from_same_ap\nHCI_FULL_PERMITION: full_permition';
        ALTER TABLE "systemrole" ADD "permition_id" VARCHAR(19);
        ALTER TABLE "systemrole" DROP COLUMN "permition";
        ALTER TABLE "systemrole" ADD CONSTRAINT "fk_systemro_permitio_4a2d38d2" FOREIGN KEY ("permition_id") REFERENCES "permition" ("slug") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "systemrole" DROP CONSTRAINT "fk_systemro_permitio_4a2d38d2";
        ALTER TABLE "systemrole" ADD "permition" VARCHAR(19)   DEFAULT 'only_from_same_cpf';
        ALTER TABLE "systemrole" DROP COLUMN "permition_id";
        DROP TABLE IF EXISTS "permition";"""
