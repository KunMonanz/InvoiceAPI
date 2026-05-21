from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from .invoice.router import router as invoice_router
from app.middleware.ratelimit_middleware import limiter

app = FastAPI()

app.include_router(invoice_router)


app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(SlowAPIMiddleware)