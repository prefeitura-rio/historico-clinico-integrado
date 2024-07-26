import pandas as pd
from typing import Callable
from loguru import logger


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
                updated_record[field] = str(content)
        elif isinstance(content, list) and depth >= list_max_depth:
            updated_record[field] = str(content)
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


def apply_formatter(records: list[dict], formatter: Callable) -> dict:
    """
    Apply a formatter function to each record in a list and return the formatted data as a dictionary of DataFrames.

    Args:
        records (list[dict]): A list of records to be formatted.
        formatter (Callable): A function that takes a record as input and returns a list of formatted rows.

    Returns:
        dict: A dictionary where the keys are table configurations and the values are DataFrames containing the formatted rows.
    """
    # Apply formatter to each record, saving result rows
    rows = []
    for record in records:
        rows.extend(formatter(record))

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
