from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from passlib.hash import pbkdf2_sha256
from jose import jwt, JWTError
from app.database import get_session_maker
from app.config import get_settings
from app.models.hotel import Hotel

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


def create_token(data: dict) -> str:
    settings = get_settings()
    data.update({"exp": datetime.utcnow() + timedelta(days=1)})
    return jwt.encode(data, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        settings = get_settings()
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        return None


async def get_current_user(request: Request):
    token = request.cookies.get("session")
    if not token:
        return None
    data = decode_token(token)
    if not data:
        return None
    return data


@router.get("/login")
async def login_page(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    async with get_session_maker()() as session:
        result = await session.execute(select(Hotel).where(Hotel.email == username))
        hotel = result.scalar_one_or_none()
        if not hotel or not pbkdf2_sha256.verify(password, hotel.password_hash):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Hatali e-posta veya sifre"})

        token = create_token({"sub": str(hotel.id), "email": hotel.email, "role": "admin" if hotel.email == "admin" else "hotel"})
        redirect = RedirectResponse(url="/dashboard", status_code=302)
        redirect.set_cookie(key="session", value=token, max_age=86400, httponly=True, samesite="lax")
        return redirect


@router.get("/logout")
async def logout():
    redirect = RedirectResponse(url="/auth/login", status_code=302)
    redirect.delete_cookie("session")
    return redirect
