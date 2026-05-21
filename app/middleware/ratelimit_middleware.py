from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

def user_or_ip(request: Request):
    user = getattr(request.state, "user", None)
    if user:
        return f"user: {user.id}"
    return get_remote_address(request)

limiter = Limiter(
    key_func=user_or_ip
)
