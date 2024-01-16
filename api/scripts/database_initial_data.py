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
    ConditionCode
)

import pandas as pd


def create_states(country, states):
    pass

def create_cities(state, cities):
    pass

async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    cids = pd.read_csv(
        "./data/cid_subcategorias.csv",
        header=0
    )

    cids_to_create = []
    for _, cid in cids.iterrows():
        cids_to_create.append(
            ConditionCode(
                type = 'cid',
                value = cid['SUBCAT'],
                description = cid['DESCRICAO']
            )
        )
    await ConditionCode.bulk_create(cids_to_create, ignore_conflicts=True)
    logger.info("CID created successfully")

    await DataSource.bulk_create([
        DataSource(system = "vitacare", cnes = "999992", description = "Teste 1")
    ], ignore_conflicts=True)
    logger.info("Data sources created successfully")

    await Gender.bulk_create([
        Gender(slug= "male", name = "Masculino"),
        Gender(slug= "female", name = "Feminino"),
        Gender(slug= "unknown", name = "Outro"),
    ], ignore_conflicts=True)
    logger.info("Genders created successfully")

    await Race.bulk_create([
        Race(slug = "parda", name = "Parda"),
        Race(slug = "branca", name = "Branca"),
        Race(slug = "preta", name = "Preta"),
        Race(slug = "amarela", name = "Amarela"),
    ], ignore_conflicts=True)
    logger.info("Races created successfully")

    await Nationality.bulk_create([
        Nationality(slug = "B", name = "Brasileiro"),
        Nationality(slug = "N", name = "Naturalizado"),
        Nationality(slug = "E", name = "Estrangeiro"),
    ], ignore_conflicts=True)
    logger.info("Nationality created successfully")

    brasil, _ = await Country.get_or_create(
        code="1", name="Brasil"
    )
    logger.info("Countries created successfully")

    relacao_estado_municipio = pd.read_csv(
        "./data/brasil_estados_municipios.csv",
        header=0
    )
    estados     = relacao_estado_municipio[['UF','Nome_UF']].drop_duplicates()
    municipios  = relacao_estado_municipio[['UF','Nome_Município','Código Município Completo']]

    cities_to_create = []
    for _, estado in estados.iterrows():
        state, _ = await State.get_or_create(
            country=brasil,
            code=estado['UF'],
            name=estado['Nome_UF']
        )

        for _, municipio in municipios[municipios['UF'] == estado['UF']].iterrows():
            cities_to_create.append(
                City(
                    state=state,
                    code=municipio['Código Município Completo'],
                    name=municipio['Nome_Município']
                )
            )
    City.bulk_create(cities_to_create, ignore_conflicts=True)
    logger.info("States and Cities created successfully")

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(run())
