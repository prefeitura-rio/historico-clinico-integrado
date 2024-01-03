# -*- coding: utf-8 -*-
from tortoise import Tortoise, run_async

from loguru import logger

from app.db import TORTOISE_ORM
from app.models import Country, DataSource, Ethnicity, Gender, Nationality, Race, State, City, AddressUse, TelecomUse, AddressType, TelecomSystem


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    data_sources = []
    for data_source_data in [{"name": "vitacare"}]:
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

    ethnicities = []
    for ethnicity_data in [{"slug": "pataxo", "name": "PATAXO"}]:
        ethnicities.append(Ethnicity(**ethnicity_data))
    await Ethnicity.bulk_create(ethnicities)
    logger.info("Ethnicity created successfully")

    nationalities = []
    for nationality_data in [{"slug": "b", "name": "B"}]:
        nationalities.append(Nationality(**nationality_data))
    await Nationality.bulk_create(nationalities)
    logger.info("Nationality created successfully")

    countries = []
    for country_data in [{"name": "Brasil"}]:
        countries.append(Country(**country_data))
    await Country.bulk_create(countries)
    logger.info("Countries created successfully")

    states = []
    for state_data in [{"name": "Rio de Janeiro", "country": await Country.get_or_none(name="Brasil")}]:
        states.append(State(**state_data))
    await State.bulk_create(states)
    logger.info("States created successfully")

    cities = []
    for city_data in [{"name": "Rio de Janeiro", "state": await State.get_or_none(name="Rio de Janeiro")}]:
        cities.append(City(**city_data))
    await City.bulk_create(cities)
    logger.info("Cities created successfully")

    addressuses = []
    for addressuse_data in [{"name": "Residencial", "slug": "home"}]:
        addressuses.append(AddressUse(**addressuse_data))
    await AddressUse.bulk_create(addressuses)
    logger.info("Address Uses created successfully")

    addresstypes = []
    for addresstype_data in [{"name": "Físico", "slug": "physical"}]:
        addresstypes.append(AddressType(**addresstype_data))
    await AddressType.bulk_create(addresstypes)
    logger.info("Address Types created successfully")

    telecomuses = []
    for telecomuse_data in [{"name": "Residencial", "slug": "home"}]:
        telecomuses.append(TelecomUse(**telecomuse_data))
    await TelecomUse.bulk_create(telecomuses)
    logger.info("telecom Uses created successfully")

    telecomsystems = []
    for telecomsystem_data in [{"name": "Celular", "slug": "phone"}]:
        telecomsystems.append(TelecomSystem(**telecomsystem_data))
    await TelecomSystem.bulk_create(telecomsystems)
    logger.info("Telecom Systems created successfully")

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(run())
