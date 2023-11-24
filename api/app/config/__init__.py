# -*- coding: utf-8 -*-
from os import getenv
from typing import List

from loguru import logger


def getenv_or_action(env_name: str, *, action: str = "raise", default: str = None) -> str:
    """Get an environment variable or raise an exception.

    Args:
        env_name (str): The name of the environment variable.
        action (str, optional): The action to take if the environment variable is not set.
            Defaults to "raise".
        default (str, optional): The default value to return if the environment variable is not set.
            Defaults to None.

    Raises:
        ValueError: If the action is not one of "raise", "warn", or "ignore".

    Returns:
        str: The value of the environment variable, or the default value if the environment variable
            is not set.
    """
    if action not in ["raise", "warn", "ignore"]:
        raise ValueError("action must be one of 'raise', 'warn', or 'ignore'")

    value = getenv(env_name, default)
    if value is None:
        if action == "raise":
            raise EnvironmentError(f"Environment variable {env_name} is not set.")
        elif action == "warn":
            logger.warning(f"Warning: Environment variable {env_name} is not set.")
    return value


def getenv_list_or_action(
    env_name: str, *, action: str = "raise", default: str = None
) -> List[str]:
    """Get an environment variable or raise an exception.

    Args:
        env_name (str): The name of the environment variable.
        action (str, optional): The action to take if the environment variable is not set.
            Defaults to "raise".
        default (str, optional): The default value to return if the environment variable is not set.
            Defaults to None.

    Raises:
        ValueError: If the action is not one of "raise", "warn", or "ignore".

    Returns:
        str: The value of the environment variable, or the default value if the environment variable
            is not set.
    """
    value = getenv_or_action(env_name, action=action, default=default)
    if value is not None:
        if isinstance(value, str):
            return value.split(",")
        elif isinstance(value, list):
            return value
        else:
            raise TypeError("value must be a string or a list")
    return []


environment = getenv_or_action("ENVIRONMENT", action="warn", default="dev")
if environment not in ["dev", "prod"]:
    raise ValueError("ENVIRONMENT must be one of 'dev' or 'prod'")

if environment == "dev":
    from app.config.dev import *  # noqa: F401, F403

else:
    from app.config.prod import *  # noqa: F401, F403
