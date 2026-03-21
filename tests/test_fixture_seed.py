import asyncio
import base64
import json

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models import Category, GroceryItem, GroceryList, Household, HouseholdMember, User
from app.services.fixture_seed import ensure_seed_data
from db_utils import dispose_db, reset_db


def _fixture_payload() -> dict[str, object]:
    return {
        "users": [
            {
                "email": "owner@example.com",
                "display_name": "Owner",
                "is_admin": True,
                "passkey": {
                    "credential_id": "owner-credential-id",
                    "public_key_b64": base64.b64encode(b"owner-public-key").decode("ascii"),
                    "sign_count": 7,
                },
            },
            {
                "email": "member@example.com",
                "display_name": "Member",
                "is_admin": False,
                "passkey": {
                    "credential_id": "member-credential-id",
                    "public_key_b64": base64.b64encode(b"member-public-key").decode("ascii"),
                    "sign_count": 3,
                },
            },
        ],
        "categories": [
            {"name": "Produce", "color": "green", "aliases": ["Veg"]},
            {"name": "Frozen", "color": "blue", "aliases": ["Ice"]},
            {"name": "Cleaning", "color": "purple", "household": "Cabin"},
        ],
        "households": [
            {
                "name": "Home",
                "owner_email": "owner@example.com",
                "members": [
                    {"email": "owner@example.com", "role": "owner"},
                    {"email": "member@example.com", "role": "member"},
                ],
                "lists": [
                    {
                        "name": "Weekly shop",
                        "created_by_email": "owner@example.com",
                        "category_order": ["Produce", "Frozen"],
                        "items": [
                            {
                                "name": "Apples",
                                "category": "Produce",
                                "quantity_text": "6",
                                "created_by_email": "owner@example.com",
                            },
                            {
                                "name": "Peas",
                                "category": "Frozen",
                                "checked": True,
                                "checked_by_email": "member@example.com",
                                "created_by_email": "owner@example.com",
                                "updated_by_email": "member@example.com",
                            },
                        ],
                    }
                ],
            },
            {
                "name": "Cabin",
                "owner_email": "member@example.com",
                "members": [{"email": "member@example.com", "role": "owner"}],
                "lists": [
                    {
                        "name": "Weekend",
                        "created_by_email": "member@example.com",
                        "category_order": ["Cleaning"],
                        "items": [
                            {
                                "name": "Soap",
                                "category": "Cleaning",
                                "note": "For guests",
                                "created_by_email": "member@example.com",
                            }
                        ],
                    }
                ],
            },
        ],
    }


def test_seed_data_populates_real_database_and_passkeys(tmp_path) -> None:
    fixture_path = tmp_path / "seed.json"
    fixture_path.write_text(json.dumps(_fixture_payload()), encoding="utf-8")
    asyncio.run(reset_db())

    async def _assert_seeded() -> None:
        async with AsyncSessionLocal() as session:
            await ensure_seed_data(session, str(fixture_path))
            await ensure_seed_data(session, str(fixture_path))

            users = (await session.execute(select(User).order_by(User.email.asc()))).scalars().all()
            assert [user.email for user in users] == ["member@example.com", "owner@example.com"]
            assert users[1].passkey_credential_id == "owner-credential-id"
            assert users[1].passkey_public_key == b"owner-public-key"
            assert users[1].passkey_sign_count == 7

            households = (
                (await session.execute(select(Household).order_by(Household.name.asc())))
                .scalars()
                .all()
            )
            assert [household.name for household in households] == ["Cabin", "Home"]

            memberships = (
                (
                    await session.execute(
                        select(HouseholdMember).order_by(HouseholdMember.role.asc())
                    )
                )
                .scalars()
                .all()
            )
            assert len(memberships) == 3

            categories = (
                (await session.execute(select(Category).order_by(Category.name.asc())))
                .scalars()
                .all()
            )
            assert [category.name for category in categories] == ["Cleaning", "Frozen", "Produce"]

            grocery_lists = (
                (await session.execute(select(GroceryList).order_by(GroceryList.name.asc())))
                .scalars()
                .all()
            )
            assert [grocery_list.name for grocery_list in grocery_lists] == [
                "Weekend",
                "Weekly shop",
            ]

            items = (
                (await session.execute(select(GroceryItem).order_by(GroceryItem.name.asc())))
                .scalars()
                .all()
            )
            assert [item.name for item in items] == ["Apples", "Peas", "Soap"]
            checked_item = next(item for item in items if item.name == "Peas")
            assert checked_item.checked is True
            assert checked_item.checked_by is not None

    try:
        asyncio.run(_assert_seeded())
    finally:
        asyncio.run(dispose_db())


def test_lifespan_runs_seed_data_fixture(monkeypatch, tmp_path) -> None:
    fixture_path = tmp_path / "seed.json"
    fixture_path.write_text(json.dumps(_fixture_payload()), encoding="utf-8")
    monkeypatch.setattr("app.main.settings.seed_data_path", str(fixture_path))
    asyncio.run(reset_db())

    try:
        from fastapi.testclient import TestClient

        with TestClient(app):
            pass

        async def _assert_seeded() -> None:
            async with AsyncSessionLocal() as session:
                users = (await session.execute(select(User))).scalars().all()
                assert len(users) == 2

        asyncio.run(_assert_seeded())
    finally:
        monkeypatch.setattr("app.main.settings.seed_data_path", None)
        asyncio.run(dispose_db())
