import json
import logging

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


def business_and_customer_key(request: Request) -> str:
    """
    Synchronous key function for SlowAPI.
    Reads values directly from request.state injected by our custom middleware.
    """
    biz_name = getattr(request.state, "rate_business_name", "none")
    cust_name = getattr(request.state, "rate_customer_name", "none")

    user = getattr(request.state, "user", None)
    identifier = f"user:{user.id}" if user else get_remote_address(request)

    if biz_name != "none" or cust_name != "none":
        return f"rate_key:{identifier}:{biz_name}:{cust_name}"

    return f"rate_key:{identifier}"


limiter = Limiter(key_func=business_and_customer_key)


class PayloadExtractorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT"):
            try:
                body_bytes = await request.body()

                if body_bytes:
                    body = json.loads(body_bytes)
                    if isinstance(body, dict):
                        cust = body.get("customer_name", "").strip().lower()
                        biz = body.get("business_name", "")

                        if cust:
                            request.state.rate_customer_name = cust
                        if biz:
                            request.state.rate_business_name = biz.strip().lower()

                async def receive():
                    return {
                        "type": "http.request",
                        "body": body_bytes,
                        "more_body": False,
                    }

                request._receive = receive

            except Exception as e:
                logger.warning(
                    f"Could not parse payload for state rate limiter tracking: {e}"
                )

        response = await call_next(request)
        return response
