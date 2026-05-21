import os
from dotenv import load_dotenv

load_dotenv()


DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "wallet_db")

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