from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

from starlette.middleware.sessions import SessionMiddleware

from authlib.integrations.starlette_client import OAuth

from .invoice.router import router as invoice_router
from .user.router import router as user_router

from app.middleware.ratelimit_middleware import limiter
from .config.settings import GOOGLE_CLIENT_ID, GOOGLE_SECRET_KEY

app = FastAPI()

app.include_router(invoice_router)
app.include_router(user_router)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler # type: ignore
)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    server_metadata_url="https://google.com",
    client_kwargs={"scope":"openid email profile"}
)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SessionMiddleware, secret_key=GOOGLE_SECRET_KEY) # type: ignore