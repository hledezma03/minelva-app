"""Endpoints de autenticación del panel admin: login y logout."""
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse

from config import config
from services.admin_service import _html_login

router = APIRouter()


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page():
    return _html_login()


@router.post("/admin/login")
async def admin_login(username: str = Form(...), password: str = Form(...), request: Request = None):
    if username == config.ADMIN_USER and password == config.ADMIN_PASS:
        request.session["admin"] = True
        return RedirectResponse(url="/static/admin.html", status_code=303)
    return HTMLResponse(content=_html_login(mostrar_error=True), status_code=401)


@router.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login")
