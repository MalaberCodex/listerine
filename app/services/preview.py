from collections.abc import Mapping
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GroceryItem, GroceryList, Household


async def fetch_preview_context(db: AsyncSession) -> Mapping[str, Any] | None:
    household_count = await db.scalar(select(func.count()).select_from(Household))
    list_count = await db.scalar(select(func.count()).select_from(GroceryList))
    item_count = await db.scalar(select(func.count()).select_from(GroceryItem))

    if household_count == 0 and list_count == 0 and item_count == 0:
        return None

    return {
        "household_count": household_count,
        "list_count": list_count,
        "item_count": item_count,
    }
