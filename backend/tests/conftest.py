import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_happyrobot.db")
os.environ.setdefault("INTERNAL_API_KEY", "test-api-key")
os.environ.setdefault("FMCSA_API_KEY", "test-fmcsa-key")
os.environ.setdefault("SEED_ON_STARTUP", "false")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "1000")
os.environ.setdefault("ALLOWED_HOSTS", "*")

from app.core.config import Settings, get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.main import create_app


@pytest.fixture(autouse=True)
async def prepare_database() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
def settings() -> Settings:
    get_settings.cache_clear()
    return Settings()


@pytest.fixture
def app(settings: Settings):
    return create_app(settings)


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
