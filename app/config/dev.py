# -*- coding: utf-8 -*-
from . import getenv_list_or_action, getenv_or_action
from .base import *  # noqa: F401, F403


# ======================
# DATABASE
# ======================
# DBO
DATABASE_HOST = getenv_or_action("DATABASE_HOST", default="localhost")
DATABASE_PORT = getenv_or_action("DATABASE_PORT", default="5432")
DATABASE_USER = getenv_or_action("DATABASE_USER", default="postgres")
DATABASE_PASSWORD = getenv_or_action("DATABASE_PASSWORD", default="postgres")
DATABASE_NAME = getenv_or_action("DATABASE_NAME", default="postgres")

# REDIS
REDIS_HOST = getenv_or_action("REDIS_HOST", action="ignore")
REDIS_PASSWORD = getenv_or_action("REDIS_PASSWORD", action="ignore")
REDIS_PORT = getenv_or_action("REDIS_PORT", action="ignore")
if REDIS_PORT:
    REDIS_PORT = int(REDIS_PORT)

# Allow to run API to use the development db from outside container
IN_DEBUGGER = getenv_or_action("IN_DEBUGGER", default="false").lower() == "true"
if IN_DEBUGGER and DATABASE_HOST == "db":
    print("Running in debugger mode, changing DATABASE_HOST to localhost")
    DATABASE_HOST = "localhost"
if IN_DEBUGGER and REDIS_HOST == "redis":
    print("Running in debugger mode, changing REDIS_HOST to localhost")
    REDIS_HOST = "localhost"

# ======================
# CORS
# ======================
ALLOWED_ORIGINS = getenv_list_or_action("ALLOWED_ORIGINS", default=["*"])
ALLOWED_ORIGINS_REGEX = None
ALLOWED_METHODS = getenv_list_or_action("ALLOWED_METHODS", default=["*"])
ALLOWED_HEADERS = getenv_list_or_action("ALLOWED_HEADERS", default=["*"])
ALLOW_CREDENTIALS = getenv_or_action("ALLOW_CREDENTIALS", default="true").lower() == "true"
