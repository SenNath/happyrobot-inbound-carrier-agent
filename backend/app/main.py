from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.extension import Limiter

from app.api.routes import router
from app.core.config import Settings, get_settings
from app.db.seed import seed_loads_if_empty
from app.db.session import SessionLocal
from app.middleware.api_key_middleware import APIKeyMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if app_settings.seed_on_startup:
            async with SessionLocal() as session:
                await seed_loads_if_empty(session)
        yield

    app = FastAPI(title=app_settings.app_name, lifespan=lifespan)

    limiter = Limiter(key_func=get_remote_address, default_limits=[f"{app_settings.rate_limit_per_minute}/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(APIKeyMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=app_settings.allowed_hosts)
    if app_settings.force_https_redirect:
        app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    )

    app.include_router(router)
    return app


app = create_app()
