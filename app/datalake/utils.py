# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
from typing import Callable
from loguru import logger
from google.cloud import bigquery

REGISTERED_FORMATTERS = {}


def register_formatter(system: str, entity: str):
    """
    Decorator function to register a formatter for a specific system and entity.

    Args:
        system (str): The name of the system.
        entity (str): The name of the entity.

    Returns:
        function: The decorated function.
    """
    def decorator(func):
        logger.info(
            f"Registering formatter for {system} - {entity}: {func.__name__}")
        REGISTERED_FORMATTERS[(system, entity)] = func
        return func
    return decorator


def get_formatter(system: str, entity: str):
    """
    Retrieves the formatter function for the specified system and entity.

    Args:
        system (str): The name of the system.
        entity (str): The name of the entity.

    Returns:
        function: The formatter function for the specified system and entity.
    """
    formatter = REGISTERED_FORMATTERS.get((system, entity))
    if not formatter:
        logger.warning(f"No formatter implemented for ({system},{entity})")
    return formatter


# Função para aplanar um dicionário
def flatten(
    record: dict,
    dict_max_depth: int = 2,
    list_max_depth: int = 1,
    depth: int = 0,
) -> dict:
    """
    Flatten a nested dictionary by concatenating keys with '__' separator.

    Args:
        record (dict): The nested dictionary to be flattened.
        dict_max_depth (int, optional): The maximum depth to flatten dictionaries.
            Defaults to 2.
        list_max_depth (int, optional): The maximum depth to flatten lists.
            Defaults to 1.
        depth (int, optional): The current depth of recursion. Defaults to 0.

    Returns:
        dict: The flattened dictionary.
    """
    updated_record = {}
    for field, content in record.items():
        if isinstance(content, dict):
            if depth < dict_max_depth:
                flattened = flatten(
                    content,
                    depth=depth + 1,
                    dict_max_depth=dict_max_depth,
                    list_max_depth=list_max_depth
                )
                for key, value in flattened.items():
                    updated_record[f"{field}__{key}"] = value
            else:
                updated_record[field] = json.dumps(content)
        elif isinstance(content, list) and depth >= list_max_depth:
            updated_record[field] = json.dumps(content)
        else:
            updated_record[field] = content

    return updated_record


def convert_model_config_to_dict(config):
    """
    Converts a model configuration object to a dictionary.

    Args:
        config: The model configuration object.

    Returns:
        A dictionary containing the configuration attributes and their values.
    """
    result = {}
    for key, value in config.__dict__.items():
        if not key.startswith("__"):
            result[key] = value
    return result


class WrongFormatException(Exception):
    pass


def apply_formatter(records: list[dict], formatter: Callable) -> dict:
    """
    Apply a formatter function to each record in a list and return the formatted data
        as a dictionary of DataFrames.

    Args:
        records (list[dict]): A list of records to be formatted.
        formatter (Callable): A function that takes a record as input and returns a
            list of formatted rows.

    Returns:
        dict: A dictionary where the keys are table configurations and the values
            are DataFrames containing the formatted rows.
    """
    # Apply formatter to each record, saving result rows
    rows = []
    for record in records:
        try:
            row = formatter(record)
            rows.extend(row)
        except Exception as e:
            raise WrongFormatException(f"Record is not in correct format: {e}")

    # Group rows by table configuration
    tables = {}
    for row in rows:
        if row.Config in tables:
            tables[row.Config].append(row.dict())
        else:
            tables[row.Config] = [row.dict()]

    # Convert each list of rows into a DataFrame
    for table_config, rows in tables.items():
        tables[table_config] = pd.DataFrame(rows)

    return tables


def generate_bigquery_schema(df: pd.DataFrame, datetime_as="TIMESTAMP") -> list[bigquery.SchemaField]:
    """
    Generates a BigQuery schema based on the provided DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame for which the BigQuery schema needs to be generated.

    Returns:
        list[bigquery.SchemaField]: The generated BigQuery schema as a list of SchemaField objects.
    """
    TYPE_MAPPING = {
        "i": "INTEGER",
        "u": "NUMERIC",
        "b": "BOOLEAN",
        "f": "FLOAT",
        "O": "STRING",
        "S": "STRING",
        "U": "STRING",
        "M": datetime_as,
    }
    schema = []
    for column, dtype in df.dtypes.items():
        val = df[column].iloc[0]
        mode = "REPEATED" if isinstance(val, list) else "NULLABLE"

        if isinstance(val, dict) or (mode == "REPEATED" and isinstance(val[0], dict)):
            fields = generate_bigquery_schema(pd.json_normalize(val))
        else:
            fields = ()

        _type = "RECORD" if fields else TYPE_MAPPING.get(dtype.kind)
        schema.append(
            bigquery.SchemaField(
                name=column,
                field_type=_type,
                mode=mode,
                fields=fields,
            )
        )
    return schema