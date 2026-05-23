import os
from dotenv import load_dotenv

from settings import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


TORTOISE_CONFIG = {
    "connections": {
        "default": f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    },
}