from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "datasource" ADD "ap" VARCHAR(2);
        ALTER TABLE "permition" ALTER COLUMN "filter_clause" SET NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "permition" ALTER COLUMN "filter_clause" DROP NOT NULL;
        ALTER TABLE "datasource" DROP COLUMN "ap";"""
