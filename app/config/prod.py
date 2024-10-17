# -*- coding: utf-8 -*-
from . import getenv_list_or_action, getenv_or_action
from .base import *  # noqa: F401, F403

# Logging
LOG_LEVEL = getenv_or_action("LOG_LEVEL", action="ignore", default="INFO")

# Database configuration
# DBO
DATABASE_HOST = getenv_or_action("DATABASE_HOST", action="raise")
DATABASE_PORT = getenv_or_action("DATABASE_PORT", action="raise")
DATABASE_USER = getenv_or_action("DATABASE_USER", action="raise")
DATABASE_PASSWORD = getenv_or_action("DATABASE_PASSWORD", action="raise")
DATABASE_NAME = getenv_or_action("DATABASE_NAME", action="raise")

# REDIS
REDIS_HOST = getenv_or_action("REDIS_HOST", action="ignore")
REDIS_PASSWORD = getenv_or_action("REDIS_PASSWORD", action="ignore")
REDIS_PORT = getenv_or_action("REDIS_PORT", action="ignore")
if REDIS_PORT:
    REDIS_PORT = int(REDIS_PORT)

# JWT configuration
if getenv_or_action("JWT_ALGORITHM", action="ignore"):
    JWT_ALGORITHM = getenv_or_action("JWT_ALGORITHM")
if getenv_or_action("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", action="ignore"):
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv_or_action("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))

# Password hashing configuration
if getenv_or_action("PASSWORD_HASH_ALGORITHM", action="ignore"):
    PASSWORD_HASH_ALGORITHM = getenv_or_action("PASSWORD_HASH_ALGORITHM")
if getenv_or_action("PASSWORD_HASH_NUMBER_OF_ITERATIONS", action="ignore"):
    PASSWORD_HASH_NUMBER_OF_ITERATIONS = int(getenv_or_action("PASSWORD_HASH_NUMBER_OF_ITERATIONS"))

# Timezone configuration
if getenv_or_action("TIMEZONE", action="ignore"):
    TIMEZONE = getenv_or_action("TIMEZONE")

# CORS configuration
ALLOWED_ORIGINS = getenv_list_or_action("ALLOWED_ORIGINS", action="ignore")
ALLOWED_ORIGINS_REGEX = None
if not ALLOWED_ORIGINS and not ALLOWED_ORIGINS_REGEX:
    raise EnvironmentError("ALLOWED_ORIGINS or ALLOWED_ORIGINS_REGEX must be set.")
ALLOWED_METHODS = getenv_list_or_action("ALLOWED_METHODS", action="raise")
ALLOWED_HEADERS = getenv_list_or_action("ALLOWED_HEADERS", action="raise")
ALLOW_CREDENTIALS = getenv_or_action("ALLOW_CREDENTIALS", action="raise").lower() == "true"

# Sentry
SENTRY_ENABLE = getenv_or_action("SENTRY_ENABLE", action="ignore").lower() == "true"
if SENTRY_ENABLE:
    SENTRY_DSN = getenv_or_action("SENTRY_DSN", action="raise")
    SENTRY_ENVIRONMENT = getenv_or_action("SENTRY_ENVIRONMENT", action="raise")
