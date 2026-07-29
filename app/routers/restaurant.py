from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.database import get_session_maker
from app.models.hotel import RestaurantOrder, MenuItem
from app.models.room import Room
from app.models.guest import Guest
from app.routers.auth import get_current_user

router = APIRouter(prefix="/restaurant", tags=["restaurant"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def restaurant_page(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user["sub"])
    async with get_session_maker()() as s:
        menu = (await s.execute(select(MenuItem).where(MenuItem.hotel_id == hid, MenuItem.available == True))).scalars().all()
        orders = (await s.execute(select(RestaurantOrder).where(RestaurantOrder.hotel_id == hid).order_by(RestaurantOrder.created_at.desc()))).scalars().all()
        rooms = {r.id: r for r in (await s.execute(select(Room).where(Room.hotel_id == hid))).scalars().all()}
    return templates.TemplateResponse("restaurant.html", {"request": request, "user": user, "menu": menu, "orders": orders, "rooms": rooms})

@router.post("/menu/add")
async def menu_add(request: Request, name: str = Form(...), price: float = Form(...), category: str = Form("")):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(MenuItem(hotel_id=int(user["sub"]), name=name, price=price, category=category or None))
        await s.commit()
    return RedirectResponse(url="/restaurant", status_code=302)

@router.post("/order/new")
async def order_create(request: Request, room_id: int = Form(0), items: str = Form(...), total: float = Form(0), notes: str = Form("")):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        s.add(RestaurantOrder(hotel_id=int(user["sub"]), room_id=room_id or None, items=items, total=total, notes=notes or None))
        await s.commit()
    return RedirectResponse(url="/restaurant", status_code=302)

@router.post("/order/{oid}/done")
async def order_done(request: Request, oid: int):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        o = (await s.execute(select(RestaurantOrder).where(RestaurantOrder.id == oid))).scalar_one_or_none()
        if o: o.status = "done"; await s.commit()
    return RedirectResponse(url="/restaurant", status_code=302)

@router.post("/menu/{mid}/toggle")
async def menu_toggle(request: Request, mid: int):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        m = (await s.execute(select(MenuItem).where(MenuItem.id == mid))).scalar_one_or_none()
        if m: m.available = not m.available; await s.commit()
    return RedirectResponse(url="/restaurant", status_code=302)
