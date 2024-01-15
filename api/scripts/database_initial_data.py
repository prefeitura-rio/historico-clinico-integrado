# -*- coding: utf-8 -*-
from loguru import logger
from tortoise import Tortoise, run_async

from app.db import TORTOISE_ORM
from app.models import (
    City,
    Country,
    DataSource,
    Gender,
    Nationality,
    Race,
    State,
)


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    data_sources = []
    for data_source_data in [{"system": "vitacare","cnes":"999999","description":"Teste 1"}]:
        data_sources.append(DataSource(**data_source_data))
    await DataSource.bulk_create(data_sources)
    logger.info("Data sources created successfully")

    genders = []
    for gender_data in [{"slug": "male", "name": "Masculino"}]:
        genders.append(Gender(**gender_data))
    await Gender.bulk_create(genders)
    logger.info("Genders created successfully")

    races = []
    for race_data in [{"slug": "parda", "name": "Parda"}]:
        races.append(Race(**race_data))
    await Race.bulk_create(races)
    logger.info("Races created successfully")

    nationalities = []
    for nationality_data in [{"slug": "B", "name": "Brasileiro"}]:
        nationalities.append(Nationality(**nationality_data))
    await Nationality.bulk_create(nationalities)
    logger.info("Nationality created successfully")

    countries = []
    for country_data in [{"name": "Brasil", "code":"00001"}]:
        countries.append(Country(**country_data))
    await Country.bulk_create(countries)
    logger.info("Countries created successfully")

    states = []
    for state_data in [
        {"name": "Rio de Janeiro",  "code":"00001", "country": await Country.get_or_none(name="Brasil")}
    ]:
        states.append(State(**state_data))
    await State.bulk_create(states)
    logger.info("States created successfully")

    cities = []
    for city_data in [
        {"name": "Rio de Janeiro", "code":"00001", "state": await State.get_or_none(name="Rio de Janeiro")}
    ]:
        cities.append(City(**city_data))
    await City.bulk_create(cities)
    logger.info("Cities created successfully")

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(run())
