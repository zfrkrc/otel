from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.database import get_session_maker
from app.models.inventory import InventoryItem
from app.routers.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["inventory"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def inventory_list(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user.get("sub", 0))
    async with get_session_maker()() as s:
        items = (await s.execute(select(InventoryItem).where(InventoryItem.hotel_id == hid))).scalars().all()
    return templates.TemplateResponse("inventory.html", {"request": request, "user": user, "items": items})

@router.post("/new")
async def inventory_create(request: Request, name: str = Form(...), category: str = Form(""), quantity: int = Form(0), min_quantity: int = Form(0), unit: str = Form(""), unit_price: float = Form(0)):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user.get("sub", 0))
    async with get_session_maker()() as s:
        s.add(InventoryItem(hotel_id=hid, name=name, category=category or None, quantity=quantity, min_quantity=min_quantity, unit=unit or None, unit_price=unit_price or None))
        await s.commit()
    return RedirectResponse(url="/inventory", status_code=302)

@router.post("/{item_id}/update")
async def inventory_update(request: Request, item_id: int, quantity: int = Form(...)):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    async with get_session_maker()() as s:
        item = (await s.execute(select(InventoryItem).where(InventoryItem.id == item_id))).scalar_one_or_none()
        if item: item.quantity = quantity; await s.commit()
    return RedirectResponse(url="/inventory", status_code=302)
