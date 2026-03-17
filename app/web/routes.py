from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
