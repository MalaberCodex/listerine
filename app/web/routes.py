from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.preview import fetch_preview_context

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html")


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "dashboard.html")


@router.get("/lists/{list_id}", response_class=HTMLResponse)
async def list_detail(request: Request, list_id: str) -> HTMLResponse:
    return templates.TemplateResponse(request, "list_detail.html", {"list_id": list_id})


@router.get("/preview", response_class=HTMLResponse)
async def preview_dashboard(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    if not settings.preview_mode:
        raise HTTPException(status_code=404)

    context = await fetch_preview_context(db)
    if context is None:
        raise HTTPException(status_code=503, detail="Preview data has not been seeded")

    return templates.TemplateResponse(request, "preview.html", context)
