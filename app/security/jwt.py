from jose import jwt, JWSError
from datetime import datetime, timedelta, timezone

from app.config.settings import JWT_ALGORITHM, JWT_SECRET_KEY


async def create_access_token(data: dict, expires_delta: timedelta):
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM) # type: ignore


async def decode_access_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]) # type: ignore