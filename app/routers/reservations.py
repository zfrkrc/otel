from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.database import get_session_maker
from app.models.reservation import Reservation
from app.models.guest import Guest
from app.models.room import Room
from app.routers.auth import get_current_user

router = APIRouter(prefix="/reservations", tags=["reservations"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def reservation_list(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user.get("sub", 0))
    async with get_session_maker()() as s:
        reservations = (await s.execute(select(Reservation).where(Reservation.hotel_id == hid).order_by(Reservation.check_in.desc()))).scalars().all()
        guests = {g.id: g for g in (await s.execute(select(Guest).where(Guest.hotel_id == hid))).scalars().all()}
        rooms = {r.id: r for r in (await s.execute(select(Room).where(Room.hotel_id == hid))).scalars().all()}
    return templates.TemplateResponse("reservations.html", {"request": request, "user": user, "reservations": reservations, "guests": guests, "rooms": rooms})

@router.get("/new")
async def reservation_new_form(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user.get("sub", 0))
    async with get_session_maker()() as s:
        guests = (await s.execute(select(Guest).where(Guest.hotel_id == hid))).scalars().all()
        rooms = (await s.execute(select(Room).where(Room.hotel_id == hid))).scalars().all()
    return templates.TemplateResponse("reservation_form.html", {"request": request, "user": user, "guests": guests, "rooms": rooms})

@router.post("/new")
async def reservation_create(request: Request, guest_id: int = Form(...), room_id: int = Form(...), check_in: str = Form(...), check_out: str = Form(...), adults: int = Form(1), notes: str = Form("")):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(Reservation(hotel_id=int(user["sub"]), guest_id=guest_id, room_id=room_id, check_in=check_in, check_out=check_out, adults=adults, notes=notes or None))
        await s.commit()
    return RedirectResponse(url="/reservations", status_code=302)

@router.post("/{rid}/status")
async def reservation_status(request: Request, rid: int, status: str = Form(...)):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        r = (await s.execute(select(Reservation).where(Reservation.id == rid))).scalar_one_or_none()
        if r: r.status = status; await s.commit()
    return RedirectResponse(url="/reservations", status_code=302)
