# -*- coding: utf-8 -*-
import json
import importlib
import pandas as pd

from loguru import logger
from tortoise import Tortoise, run_async
from app.db import TORTOISE_ORM

from app.models import TableInitialization


async def run():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    metas = json.load(open("./data/meta.json"))

    for tablemeta in metas:
        table, _ = await TableInitialization.get_or_create(
            table_name=tablemeta['table_name']
        )
        
        if (table.last_version is None) or (tablemeta['version'] > table.last_version):
            table.last_version = tablemeta['version']
            await table.save()

            module = importlib.import_module('app.models')
            ModelClass = getattr(module, tablemeta['entity_model_name'])

            initial_data = pd.read_csv(
                tablemeta['source_csv_name'],
                header=0,
                dtype=str
            )

            new_instances = []
            for _, row in initial_data.iterrows():
                kwargs = row.to_dict()
                instance = ModelClass(**kwargs)
                new_instances.append(instance)

            await ModelClass.bulk_create(
                new_instances,
                on_conflict=tablemeta['conflict_columns'],
                update_fields=initial_data.columns.tolist()
            )

            logger.info(f"{tablemeta['entity_model_name']} initialized successfully")
        else:
            logger.info(f"{tablemeta['entity_model_name']} is up to date!")

    await Tortoise.close_connections()


if __name__ == "__main__":
    
    run_async(
        run()
    )