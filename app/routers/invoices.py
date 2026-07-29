from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from app.database import get_session_maker
from app.models.invoice import Invoice
from app.models.guest import Guest
from app.models.reservation import Reservation
from app.routers.auth import get_current_user

router = APIRouter(prefix="/invoices", tags=["invoices"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
async def invoice_list(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user.get("sub", 0))
    async with get_session_maker()() as s:
        invoices = (await s.execute(select(Invoice).where(Invoice.hotel_id == hid).order_by(Invoice.created_at.desc()))).scalars().all()
        guests = {g.id: g for g in (await s.execute(select(Guest).where(Guest.hotel_id == hid))).scalars().all()}
    return templates.TemplateResponse("invoices.html", {"request": request, "user": user, "invoices": invoices, "guests": guests})

@router.post("/new")
async def invoice_create(request: Request, guest_id: int = Form(...), amount: float = Form(...), payment_method: str = Form("cash"), notes: str = Form("")):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    hid = int(user.get("sub", 0))
    async with get_session_maker()() as s:
        import uuid
        s.add(Invoice(hotel_id=hid, guest_id=guest_id, invoice_no=f"INV-{uuid.uuid4().hex[:8].upper()}", amount=amount, tax=0, total=amount, payment_method=payment_method, notes=notes or None, status="paid"))
        await s.commit()
    return RedirectResponse(url="/invoices", status_code=302)
