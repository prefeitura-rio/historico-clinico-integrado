# -*- coding: utf-8 -*-
import argparse
import importlib
import pandas as pd
from loguru import logger
from tortoise import Tortoise, run_async

from app.db import TORTOISE_ORM


parser = argparse.ArgumentParser(description="Initialize a specific entity")
parser.add_argument(
    "--entity-model-name",
    type=str,
    help="The Entity model name to initialize",
    required=True
)
parser.add_argument(
    "--source-csv-name",
    type=str,
    help="The name of the CSV file used to populate the table",
    required=True
)
parser.add_argument(
    "--conflict-column",
    type=str,
    nargs='+',
    help="The column name used to detect Conflicts",
    required=True
)
parser.add_argument(
    "--exclude-in-update",
    type=str,
    nargs='+',
    help="In case of conflicts, do not update this field",
    required=False
)


async def run(
    entity_model_name: str,
    source_csv_name: str,
    conflict_columns: list[str],
    exclude_in_update: list[str] = None
):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    file_path = f"./data/{source_csv_name}.csv"
    module = importlib.import_module('app.models')
    ModelClass = getattr(module, entity_model_name)

    logger.info(f"Beginning Table Init: {entity_model_name} from {file_path}")

    initial_data = pd.read_csv(
        file_path,
        header=0,
        dtype=str
    )

    new_instances = []
    for _, row in initial_data.iterrows():
        kwargs = row.to_dict()
        instance = ModelClass(**kwargs)
        new_instances.append(instance)

    updatable_columns = initial_data.columns.tolist()
    if exclude_in_update and exclude_in_update in updatable_columns:
        updatable_columns.remove(exclude_in_update)

    await ModelClass.bulk_create(
        new_instances,
        on_conflict=conflict_columns,
        update_fields=updatable_columns
    )
    logger.info(f"{entity_model_name} created successfully")

    await Tortoise.close_connections()


if __name__ == "__main__":
    args = parser.parse_args()

    run_async(
        run(
            entity_model_name=args.entity_model_name,
            source_csv_name=args.source_csv_name,
            conflict_columns=args.conflict_column,
            exclude_in_update=args.exclude_in_update
        )
    )