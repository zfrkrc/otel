from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.database import get_session_maker
from app.models.guest import Guest
from app.routers.auth import get_current_user

router = APIRouter(prefix="/guests", tags=["guests"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def guest_list(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user.get("sub", 0))
    async with get_session_maker()() as s:
        guests = (await s.execute(select(Guest).where(Guest.hotel_id == hid))).scalars().all()
    return templates.TemplateResponse("guests.html", {"request": request, "user": user, "guests": guests})

@router.post("/new")
async def guest_create(request: Request, first_name: str = Form(...), last_name: str = Form(...), email: str = Form(""), phone: str = Form(""), id_card: str = Form("")):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(Guest(hotel_id=int(user["sub"]), first_name=first_name, last_name=last_name, email=email or None, phone=phone or None, id_card=id_card or None))
        await s.commit()
    return RedirectResponse(url="/guests", status_code=302)
