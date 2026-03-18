import asyncio

from fastapi.testclient import TestClient

from app.core.database import Base, AsyncSessionLocal, engine
from app.main import app
from app.services.preview import ensure_preview_seed_data


async def _reset_and_seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await ensure_preview_seed_data(session)


def test_preview_page_renders_seeded_data(monkeypatch) -> None:
    monkeypatch.setattr("app.web.routes.settings.preview_mode", True)
    asyncio.run(_reset_and_seed())

    with TestClient(app) as client:
        response = client.get("/preview")

    assert response.status_code == 200
    assert "Preview Household" in response.text
    assert "Weekend Shop" in response.text
    assert "Bananas" in response.text
