# -*- coding: utf-8 -*-
from loguru import logger
from tortoise import Tortoise, run_async
from tortoise.models import Model

from api.app.models import mrg
from app.db import TORTOISE_ORM


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    # Clean up database
    for _, v in mrg.__dict__.items():
        if isinstance(v, type) and issubclass(v, Model) and v != Model:
            logger.info(f"Cleaning up {v.__name__}")
            await v.all().delete()

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(run())
