from settings import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

if not DB_HOST:
    raise Exception("DB_HOST missing")
if not DB_NAME:
    raise Exception("DB_NAME missing")
if not DB_PASS:
    raise Exception("DB_PASS missing")
if not DB_PORT:
    raise Exception("DB_PORT missing")
if not DB_USER:
    raise Exception("DB_USER missing")


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