import pandas as pd
from loguru import logger


# Dicionário global para armazenar os formatters
formatters = {}

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
        logger.info(f"Registering formatter for {system} - {entity}: {func.__name__}")
        formatters[(system, entity)] = func
        return func
    return decorator


# Função para acessar o formatter
def get_formatter(system: str, entity: str):
    """
    Retrieves the formatter function for the specified system and entity.

    Args:
        system (str): The name of the system.
        entity (str): The name of the entity.

    Returns:
        function: The formatter function for the specified system and entity.

    Raises:
        AssertionError: If the formatter for the specified system and entity is not found.
    """
    assert (system, entity) in formatters, f"Formatter for {system} - {entity} not found"
    return formatters.get((system, entity))


# Função para aplanar um dicionário
def flatten(
    record: dict,
    max_depth: int = 2,
    depth: int = 0,
) -> dict:
    """
    Flattens a nested dictionary by concatenating keys with '__' separator.
    
    Args:
        record (dict): The nested dictionary to be flattened.
        max_depth (int, optional): The maximum depth to flatten. Defaults to 2.
        depth (int, optional): The current depth of recursion. Defaults to 0.
    
    Returns:
        dict: The flattened dictionary.
    """
    updated_record = {}
    for field, content in record.items():
        if isinstance(content, dict):
            if depth < max_depth:
                for key, value in flatten(content, depth=depth + 1).items():
                    updated_record[f"{field}__{key}"] = value
            else:
                updated_record[field] = str(content)
        elif isinstance(content, list) and depth > 1:
            updated_record[field] = str(content)
        else:
            updated_record[field] = content
    
    return updated_record


def apply_formatter(records:list[dict], formatter) -> dict:
    tables = {}

    for record in records:
        for row_set in formatter(record):
            for row in row_set:
                if row.Config in tables:
                    tables[row.Config].append(row)
                else:
                    tables[row.Config] = [row]
    
    for table_config, rows in tables.items():
        tables[table_config] = pd.DataFrame([row.dict() for row in rows])
    
    return tables