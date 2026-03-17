import asyncio

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app


async def _reset_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture()
def client() -> TestClient:
    asyncio.run(_reset_db())
    with TestClient(app) as test_client:
        yield test_client
