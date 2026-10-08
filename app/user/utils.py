import hashlib
import hmac
import time

from fastapi import HTTPException, Request, status


def get_jwt_from_headers(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return auth_header.split(" ")[1]


def verify_cron_signature(
    timestamp: str, client_signature: str, secret_key: str, max_age_seconds: int = 300
):
    """
    Verifies that an incoming request was signed using a shared secret and a valid timestamp.
    Prevents replay attacks by checking request freshness.
    """
    try:
        request_time = int(timestamp)
        current_time = int(time.time())
        if abs(current_time - request_time) > max_age_seconds:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Signature expired"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid timestamp format"
        )

    message = f"{timestamp}:cron-cleanup".encode("utf-8")

    expected_signature = hmac.new(
        key=secret_key.encode("utf-8"), msg=message, digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, client_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature validation",
        )
