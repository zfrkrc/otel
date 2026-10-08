# Otel — Otel Yönetim (PMS)

Çok-kiracılı (multi-tenant) otel yönetim sistemi: oda, rezervasyon, giriş/çıkış,
misafir ve raporlama. FastAPI + Jinja2 şablonları ile sunucu taraflı (SSR).

## Teknoloji
- **FastAPI** (0.115) + **Uvicorn**
- **SQLAlchemy (async)** + **asyncpg** → PostgreSQL 16
- **Jinja2** şablonları (admin + hotel panelleri)
- Kimlik: JWT (`python-jose`) + parola hash (`passlib[bcrypt]`)

## Yapı
```
app/
  main.py            # FastAPI uygulaması
  config.py          # ayarlar (env)
  database.py        # async DB oturumu
  routers/           # admin + hotel + public route'lar
  models/            # SQLAlchemy modelleri
  services/          # iş mantığı
  templates/         # admin/ ve hotel/ Jinja2 şablonları
  static/            # css/varlıklar
docker/              # docker yardımcıları
docker-compose.yml   # app + postgres
Dockerfile
requirements.txt
```

## Çalıştırma (Docker)
```bash
docker compose up -d --build
# http://localhost:8200
```

## Ortam değişkenleri
- `DATABASE_URL` — örn. `postgresql+asyncpg://otel:otel_pass@postgres:5432/otel`
- `SECRET_KEY` — JWT/oturum anahtarı (üretimde değiştir)

## Notlar
- Public URL: `otel.zk.net.tr` (Cloudflare Access arkasında).
- Multi-tenant: her otel ayrı kiracı; admin ve hotel panelleri ayrı.
