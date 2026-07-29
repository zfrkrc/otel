from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func as sf
from datetime import date, timedelta
from app.database import get_session_maker
from app.models.room import Room, RoomType
from app.models.reservation import Reservation
from app.models.guest import Guest
from app.models.invoice import Invoice
from app.models.inventory import InventoryItem
from app.models.hotel import HousekeepingTask
from app.routers.auth import get_current_user

router = APIRouter(tags=["analytics"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/calendar")
async def calendar_view(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user["sub"])
    async with get_session_maker()() as s:
        rooms = (await s.execute(select(Room).where(Room.hotel_id == hid))).scalars().all()
        reservations = (await s.execute(select(Reservation).where(Reservation.hotel_id == hid))).scalars().all()
    return templates.TemplateResponse("calendar.html", {"request": request, "user": user, "rooms": rooms, "reservations": reservations})

@router.get("/api/availability")
async def availability_api(request: Request, year: int = 0, month: int = 0):
    user = await get_current_user(request)
    if not user: return {"error": "auth"}
    hid = int(user["sub"])
    today = date.today()
    y, m = (year, month) if year else (today.year, today.month)
    async with get_session_maker()() as s:
        rooms = (await s.execute(select(Room).where(Room.hotel_id == hid))).scalars().all()
        res = (await s.execute(select(Reservation).where(Reservation.hotel_id == hid))).scalars().all()
    days = []
    import calendar as cal
    for d in cal.Calendar().itermonthdates(y, m):
        if d.month != m: continue
        booked = sum(1 for r in res if r.room_id and r.check_in <= d <= r.check_out and r.status not in ("cancelled",))
        available = len(rooms) - booked
        days.append({"date": d.isoformat(), "available": available, "booked": booked, "total": len(rooms)})
    return {"days": days, "total_rooms": len(rooms)}

@router.get("/api/stats")
async def stats_api(request: Request):
    user = await get_current_user(request)
    if not user: return {"error": "auth"}
    hid = int(user["sub"])
    async with get_session_maker()() as s:
        total_rooms = (await s.execute(select(sf.count(Room.id)).where(Room.hotel_id == hid))).scalar() or 0
        total_guests = (await s.execute(select(sf.count(Guest.id)).where(Guest.hotel_id == hid))).scalar() or 0
        active_res = (await s.execute(select(sf.count(Reservation.id)).where(Reservation.hotel_id == hid, Reservation.status.in_(["confirmed","checked_in"])))).scalar() or 0
        revenue = (await s.execute(select(sf.coalesce(sf.sum(Invoice.total), 0)).where(Invoice.hotel_id == hid))).scalar() or 0
        low_stock = (await s.execute(select(sf.count(InventoryItem.id)).where(InventoryItem.hotel_id == hid, InventoryItem.quantity <= InventoryItem.min_quantity))).scalar() or 0
        pending_hk = (await s.execute(select(sf.count(HousekeepingTask.id)).where(HousekeepingTask.hotel_id == hid, HousekeepingTask.status == "pending"))).scalar() or 0
    return {"total_rooms": total_rooms, "total_guests": total_guests, "active_reservations": active_res, "revenue": revenue, "low_stock": low_stock, "pending_housekeeping": pending_hk}
