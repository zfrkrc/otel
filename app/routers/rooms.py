from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.database import get_session_maker
from app.models.room import RoomType, Room
from app.routers.auth import get_current_user

router = APIRouter(prefix="/rooms", tags=["rooms"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def room_list(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user["sub"])
    async with get_session_maker()() as s:
        types = (await s.execute(select(RoomType).where(RoomType.hotel_id == hid))).scalars().all()
        rooms = (await s.execute(select(Room).where(Room.hotel_id == hid).order_by(Room.room_number))).scalars().all()
    return templates.TemplateResponse("rooms.html", {"request": request, "user": user, "types": types, "rooms": rooms})

@router.post("/type/new")
async def type_create(request: Request, name: str = Form(...), base_price: float = Form(...), capacity: int = Form(2), description: str = Form(""), amenities: str = Form("")):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(RoomType(hotel_id=int(user["sub"]), name=name, base_price=base_price, capacity=capacity, description=description or None, amenities=amenities or None))
        await s.commit()
    return RedirectResponse(url="/rooms", status_code=302)

@router.post("/new")
async def room_create(request: Request, room_number: str = Form(...), room_type_id: int = Form(0), floor: int = Form(0)):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(Room(hotel_id=int(user["sub"]), room_number=room_number, room_type_id=room_type_id or None, floor=floor or None))
        await s.commit()
    return RedirectResponse(url="/rooms", status_code=302)

@router.post("/bulk")
async def room_bulk_create(request: Request, prefix: str = Form(...), start: int = Form(...), end: int = Form(...), room_type_id: int = Form(0), floor: int = Form(0)):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user["sub"])
    if end - start > 500:
        return RedirectResponse(url="/rooms?error=500+oden+fazla+tek+seferde+eklenemez", status_code=302)
    created = 0
    async with get_session_maker()() as s:
        for num in range(start, end + 1):
            rn = f"{prefix}{num:03d}" if prefix.isalpha() else f"{prefix}{num}"
            existing = (await s.execute(select(Room).where(Room.hotel_id == hid, Room.room_number == rn))).scalar_one_or_none()
            if not existing:
                s.add(Room(hotel_id=hid, room_number=rn, room_type_id=room_type_id or None, floor=floor or None))
                created += 1
        await s.commit()
    return RedirectResponse(url=f"/rooms?success={created}+oda+olusturuldu", status_code=302)

@router.post("/{room_id}/delete")
async def room_delete(request: Request, room_id: int):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        r = (await s.execute(select(Room).where(Room.id == room_id))).scalar_one_or_none()
        if r: await s.delete(r); await s.commit()
    return RedirectResponse(url="/rooms", status_code=302)
