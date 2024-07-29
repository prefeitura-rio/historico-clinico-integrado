# -*- coding: utf-8 -*-
from secrets import token_bytes

from . import getenv_or_action

# Logging
LOG_LEVEL = getenv_or_action("LOG_LEVEL", default="INFO")

# JWT configuration
JWT_SECRET_KEY = getenv_or_action("JWT_SECRET_KEY", default=token_bytes(32).hex())
JWT_ALGORITHM = getenv_or_action("JWT_ALGORITHM", default="HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    getenv_or_action("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default="30")
)

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
