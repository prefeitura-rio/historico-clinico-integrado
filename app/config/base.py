# -*- coding: utf-8 -*-
from secrets import token_bytes

from . import getenv_or_action

# Logging
LOG_LEVEL = getenv_or_action("LOG_LEVEL", default="INFO")

# BigQuery Integration
BIGQUERY_PROJECT = getenv_or_action("BIGQUERY_PROJECT", action="raise")
BIGQUERY_PATIENT_HEADER_TABLE_ID = getenv_or_action(
    "BIGQUERY_PATIENT_HEADER_TABLE_ID", action="raise"
)
BIGQUERY_PATIENT_SUMMARY_TABLE_ID = getenv_or_action(
    "BIGQUERY_PATIENT_SUMMARY_TABLE_ID", action="raise"
)
BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID = getenv_or_action(
    "BIGQUERY_PATIENT_ENCOUNTERS_TABLE_ID", action="raise"
)
BIGQUERY_ERGON_TABLE_ID = getenv_or_action("BIGQUERY_ERGON_TABLE_ID", action="raise")
BIGQUERY_ACCESS_TABLE_ID = getenv_or_action("BIGQUERY_ACCESS_TABLE_ID", action="raise")
BIGQUERY_PATIENT_SEARCH_TABLE_ID = getenv_or_action("BIGQUERY_PATIENT_SEARCH_TABLE_ID", action="raise")
BIGQUERY_PATIENT_INDEX_TABLE_ID = getenv_or_action("BIGQUERY_PATIENT_INDEX_TABLE_ID", action="raise")

# JWT configuration
JWT_SECRET_KEY = getenv_or_action("JWT_SECRET_KEY", default=token_bytes(32).hex())
JWT_ALGORITHM = getenv_or_action("JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    getenv_or_action("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default="30")
)

# Auth
DATARELAY_URL = getenv_or_action("DATARELAY_URL", action="raise")
DATARELAY_MAILMAN_TOKEN = getenv_or_action("DATARELAY_MAILMAN_TOKEN", action="raise")
EMAIL_SUBJECT_2FA = getenv_or_action("EMAIL_SUBJECT_2FA", action="raise")
EMAIL_BODY_2FA = getenv_or_action("EMAIL_BODY_2FA", action="raise")

# Vitacare 
VITACARE_HASHED_PASSWORD = getenv_or_action("VITACARE_HASHED_PASSWORD", action="raise")
VITACARE_USERNAME = getenv_or_action("VITACARE_USERNAME", action="raise")
DATALAKE_HUB_URL = getenv_or_action("DATALAKE_HUB_URL", action="raise")
DATALAKE_HUB_USERNAME = getenv_or_action("DATALAKE_HUB_USERNAME", action="raise")
DATALAKE_HUB_PASSWORD = getenv_or_action("DATALAKE_HUB_PASSWORD", action="raise")

# GOVBR
GOVBR_PROVIDER_URL = getenv_or_action("GOVBR_PROVIDER_URL", action="raise")
GOVBR_CLIENT_ID = getenv_or_action("GOVBR_CLIENT_ID", action="raise")
GOVBR_CLIENT_SECRET = getenv_or_action("GOVBR_CLIENT_SECRET", action="raise")
GOVBR_REDIRECT_URL = getenv_or_action("GOVBR_REDIRECT_URL", action="raise")

# Request Limit Configuration
REQUEST_LIMIT_MAX = int(getenv_or_action("REQUEST_LIMIT_MAX", action="raise"))
REQUEST_LIMIT_WINDOW_SIZE = int(getenv_or_action("REQUEST_LIMIT_WINDOW_SIZE", action="raise"))

# Timezone configuration

TIMEZONE = "America/Sao_Paulo"

# Sentry
SENTRY_ENABLE = False
SENTRY_DSN = None
SENTRY_ENVIRONMENT = None

# Cache
CACHE_ENABLE = getenv_or_action("CACHE_ENABLE", default="false").lower() == "true"
if CACHE_ENABLE:
    CACHE_REDIS_HOST = getenv_or_action("CACHE_REDIS_HOST", action="raise")
    CACHE_REDIS_PORT = int(getenv_or_action("CACHE_REDIS_PORT", action="raise"))
    CACHE_REDIS_PASSWORD = getenv_or_action("CACHE_REDIS_PASSWORD", action="raise")
    CACHE_REDIS_DB = int(getenv_or_action("CACHE_REDIS_DB", action="raise"))
else:
    CACHE_REDIS_HOST = None
    CACHE_REDIS_PORT = None
    CACHE_REDIS_PASSWORD = None
    CACHE_REDIS_DB = None
CACHE_DEFAULT_TIMEOUT = int(getenv_or_action("CACHE_DEFAULT_TIMEOUT", default="43200"))  # 12 hours
