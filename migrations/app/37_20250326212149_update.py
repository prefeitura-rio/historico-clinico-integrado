from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "password" VARCHAR(255);
        ALTER TABLE "user" ALTER COLUMN "email" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "password";
        ALTER TABLE "user" ALTER COLUMN "email" SET NOT NULL;"""
