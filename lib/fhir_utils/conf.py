# -*- coding: utf-8 -*-
from os import getenv
from typing import Callable, Union

from loguru import logger


def getenv_or_action(
    key: str, action: Union[Callable[[str], str], str], default: str = None
) -> str:
    """
    Get an environment variable or execute an action.

    Args:
        key (str): The name of the environment variable.
        action (Union[Callable[[str], str], str]): The action to execute if the
            environment variable is not set. Can be a callable or a string. If a
            callable is provided, it will be called with the key as the only
            argument. If a string is provided, it will check if this callback
            is implemented here and call it. If not, it will raise an exception.
        default (str, optional): The default value to return if the environment
            variable is not set and no action is provided. Defaults to None.

    Returns:
        str: The value of the environment variable or the result of the action.
    """

    def _raise(key: str) -> str:
        raise Exception(
            f"Environment variable {key} is not set and no action is provided."
        )

    def _warn(key: str) -> str:
        logger.warning(f"Environment variable {key} is not set. Using default value.")
        return default

    def _pass(key: str) -> str:
        return default

    _val = getenv(key)
    if _val is None:
        if action in [None, "pass"]:
            return _pass(key)
        elif callable(action):
            return action(key)
        elif isinstance(action, str):
            if action == "raise":
                return _raise(key)
            elif action == "warn":
                return _warn(key)
            else:
                raise ValueError(
                    f'Action "{action}" is not implemented in getenv_or_action.'
                )
        else:
            return default
    return _val


class Settings:
    __slots__ = ()


settings = Settings()
