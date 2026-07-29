from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from datetime import date
from app.database import get_session_maker
from app.models.hotel import HousekeepingTask
from app.models.room import Room
from app.routers.auth import get_current_user

router = APIRouter(prefix="/housekeeping", tags=["housekeeping"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def hk_list(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user["sub"])
    async with get_session_maker()() as s:
        tasks = (await s.execute(select(HousekeepingTask).where(HousekeepingTask.hotel_id == hid).order_by(HousekeepingTask.date.desc()))).scalars().all()
        rooms = {r.id: r for r in (await s.execute(select(Room).where(Room.hotel_id == hid))).scalars().all()}
    return templates.TemplateResponse("housekeeping.html", {"request": request, "user": user, "tasks": tasks, "rooms": rooms, "today": date.today()})

@router.post("/new")
async def hk_create(request: Request, room_id: int = Form(...), date: str = Form(...), assigned_to: str = Form(""), priority: str = Form("normal"), notes: str = Form("")):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(HousekeepingTask(hotel_id=int(user["sub"]), room_id=room_id, date=date, assigned_to=assigned_to or None, priority=priority, notes=notes or None))
        await s.commit()
    return RedirectResponse(url="/housekeeping", status_code=302)

@router.post("/{task_id}/done")
async def hk_done(request: Request, task_id: int):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        t = (await s.execute(select(HousekeepingTask).where(HousekeepingTask.id == task_id))).scalar_one_or_none()
        if t: t.status = "done"; await s.commit()
    return RedirectResponse(url="/housekeeping", status_code=302)
