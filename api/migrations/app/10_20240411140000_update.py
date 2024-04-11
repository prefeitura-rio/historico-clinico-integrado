from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "meta__tableinitialization" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "table_name" VARCHAR(255) NOT NULL UNIQUE,
    "last_version" INT NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "meta__tableinitialization";"""
