from contextlib import asynccontextmanager

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config.settings import settings
from app.invoice.router import router as invoice_router
from app.middleware.ratelimit_middleware import PayloadExtractorMiddleware, limiter
from app.scheduler import start_scheduler
from app.user.admin_router import admin_router
from app.user.router import router as user_router

if settings.ENVIRONMENT == "production":
    docs_url = None
    redoc_url = None
    openapi_url = None
else:
    docs_url = "/docs"
    redoc_url = "/redoc"
    openapi_url = "/openapi.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield


app = FastAPI(
    lifespan=lifespan, docs_url=docs_url, redoc_url=redoc_url, openapi_url=openapi_url
)

app.include_router(invoice_router)
app.include_router(user_router)
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://invoice-frontend-ecru-three.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,  # type: ignore
)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    server_metadata_url="https://google.com",
    client_kwargs={"scope": "openid email profile"},
)
app.add_middleware(PayloadExtractorMiddleware)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.GOOGLE_SECRET_KEY)
