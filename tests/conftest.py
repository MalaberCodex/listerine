import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import close_all_sessions

from app.core.database import Base, engine
from app.main import app


async def _reset_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _dispose_db() -> None:
    await close_all_sessions()
    await engine.dispose()


@pytest.fixture()
def client() -> TestClient:
    asyncio.run(_reset_db())
    with TestClient(app) as test_client:
        yield test_client
    asyncio.run(_dispose_db())
