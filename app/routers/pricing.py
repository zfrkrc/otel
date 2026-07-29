from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.database import get_session_maker
from app.models.room import RoomType, SeasonalPrice
from app.routers.auth import get_current_user

router = APIRouter(prefix="/pricing", tags=["pricing"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def pricing_list(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user["sub"])
    async with get_session_maker()() as s:
        types = (await s.execute(select(RoomType).where(RoomType.hotel_id == hid))).scalars().all()
        prices = (await s.execute(select(SeasonalPrice).where(SeasonalPrice.hotel_id == hid).order_by(SeasonalPrice.date_from))).scalars().all()
    return templates.TemplateResponse("pricing.html", {"request": request, "user": user, "types": types, "prices": prices})

@router.post("/new")
async def pricing_create(request: Request, room_type_id: int = Form(...), name: str = Form(""), date_from: str = Form(...), date_to: str = Form(...), price: float = Form(...)):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(SeasonalPrice(hotel_id=int(user["sub"]), room_type_id=room_type_id, name=name or None, date_from=date_from, date_to=date_to, price=price))
        await s.commit()
    return RedirectResponse(url="/pricing", status_code=302)

@router.post("/{pid}/delete")
async def pricing_delete(request: Request, pid: int):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        p = (await s.execute(select(SeasonalPrice).where(SeasonalPrice.id == pid))).scalar_one_or_none()
        if p: await s.delete(p); await s.commit()
    return RedirectResponse(url="/pricing", status_code=302)
