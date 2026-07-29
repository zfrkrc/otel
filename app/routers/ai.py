from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
from app.routers.auth import get_current_user

router = APIRouter(prefix="/ai", tags=["ai"])
templates = Jinja2Templates(directory="app/templates")

OLLAMA_HOST = "https://insightmap.tr"


@router.get("/assistant")
async def ai_page(request: Request):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse("ai.html", {"request": request, "user": user, "result": "", "prompt": ""})


@router.post("/assistant")
async def ai_ask(request: Request, prompt: str = Form(...)):
    user = await get_current_user(request)
    if not user: return RedirectResponse(url="/auth/login", status_code=302)

    system = "Sen bir otel yonetim asistanisin. Otelcilik, rezervasyon yonetimi, misafir iliskileri, fiyatlama stratejileri ve otel operasyonlari hakkinda yardimci ol. Turkce cevap ver."
    full_prompt = f"{system}\n\nSoru: {prompt}\n\nCevap:"

    try:
        async with httpx.AsyncClient(timeout=120, verify=False) as client:
            resp = await client.post(f"{OLLAMA_HOST}/api/ollama/generate", json={
                "model": "qwen2.5:14b",
                "prompt": full_prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 1024},
            })
            result = resp.json().get("response", "") if resp.status_code == 200 else "AI su an kullanilamiyor."
    except:
        result = "AI servisine ulasilamadi."

    return templates.TemplateResponse("ai.html", {"request": request, "user": user, "result": result, "prompt": prompt})
