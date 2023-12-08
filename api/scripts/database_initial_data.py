# -*- coding: utf-8 -*-
from tortoise import Tortoise, run_async

from loguru import logger

from app.db import TORTOISE_ORM
from app.models import City, Country, DataSource, Ethnicity, Gender, Nationality, Race, State


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    # TODO: Create initial data
    data_sources = []
    for data_source_data in [{"name": "vitacare"}]:
        data_sources.append(DataSource(**data_source_data))
    await DataSource.bulk_create(data_sources)
    logger.info("Data sources created successfully")
    genders = []
    for gender_data in [{"slug": "male", "name": "male"}]:
        genders.append(Gender(**gender_data))
    await Gender.bulk_create(genders)
    logger.info("Genders created successfully")

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(run())
