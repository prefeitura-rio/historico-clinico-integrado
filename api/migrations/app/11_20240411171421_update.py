from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "meta__tableinitialization" ALTER COLUMN "last_version" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "meta__tableinitialization" ALTER COLUMN "last_version" SET NOT NULL;"""
