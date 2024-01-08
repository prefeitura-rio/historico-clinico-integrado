# -*- coding: utf-8 -*-
from app import config

TORTOISE_ORM = {
    "connections": {"default": config.DATABASE_URL},
    "apps": {
        "app": {
            "models": [
                "aerich.models",
                "app.models.raw",
                "app.models.std",
                "app.models.mrg"
            ],
            "default_connection": "default",
        },
    },
}
