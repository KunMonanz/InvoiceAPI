from settings import settings

TORTOISE_CONFIG = {
    "connections": {
        "default": settings.TORTOISE_DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
