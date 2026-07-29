from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import init_db, close_db
from app.config import get_settings
from app.routers import auth, dashboard, rooms, guests, reservations, invoices, inventory, analytics, housekeeping, pricing, ai, restaurant, issues


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="OtelSaaS", lifespan=lifespan)
settings = get_settings()

if not settings.secret_key:
    raise RuntimeError("SECRET_KEY must be set in .env")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(rooms.router)
app.include_router(guests.router)
app.include_router(reservations.router)
app.include_router(invoices.router)
app.include_router(inventory.router)
app.include_router(analytics.router)
app.include_router(housekeeping.router)
app.include_router(pricing.router)
app.include_router(ai.router)
app.include_router(restaurant.router)
app.include_router(issues.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/auth/login")


@app.get("/health")
async def health():
    return {"status": "healthy"}
