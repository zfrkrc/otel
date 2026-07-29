from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from datetime import datetime
from app.database import get_session_maker
from app.models.hotel import HotelIssue
from app.models.room import Room
from app.routers.auth import get_current_user

router = APIRouter(prefix="/issues", tags=["issues"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def issue_list(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user["sub"])
    async with get_session_maker()() as s:
        issues = (await s.execute(select(HotelIssue).where(HotelIssue.hotel_id == hid).order_by(HotelIssue.created_at.desc()))).scalars().all()
        rooms = {r.id: r for r in (await s.execute(select(Room).where(Room.hotel_id == hid))).scalars().all()}
    return templates.TemplateResponse("issues.html", {"request": request, "user": user, "issues": issues, "rooms": rooms})

@router.post("/new")
async def issue_create(request: Request, title: str = Form(...), room_id: int = Form(0), description: str = Form(""), priority: str = Form("normal")):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(HotelIssue(hotel_id=int(user["sub"]), room_id=room_id or None, title=title, description=description or None, priority=priority))
        await s.commit()
    return RedirectResponse(url="/issues", status_code=302)

@router.post("/{iid}/resolve")
async def issue_resolve(request: Request, iid: int):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        i = (await s.execute(select(HotelIssue).where(HotelIssue.id == iid))).scalar_one_or_none()
        if i: i.status = "resolved"; i.resolved_at = datetime.now(); await s.commit()
    return RedirectResponse(url="/issues", status_code=302)
