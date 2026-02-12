from fastapi import HTTPException, Request, status

from app.core.config import get_settings


EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


def validate_api_key(request: Request) -> None:
    if request.method == "OPTIONS":
        return

    if request.url.path in EXEMPT_PATHS:
        return

    provided_key = request.headers.get("x-api-key")
    expected_key = get_settings().internal_api_key
    if not provided_key or provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
