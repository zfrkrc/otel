# Otel — SRS + SDD (Spec)

## 1. Amaç / Kapsam
Çok-kiracılı **otel yönetim sistemi (PMS)**: oda, rezervasyon, giriş/çıkış, misafir,
raporlama. FastAPI + Jinja2 (SSR).

## 2. Aktörler
- **Otel yöneticisi** — oda/rezervasyon/fiyat (`hotel/` panel).
- **Resepsiyon** — giriş/çıkış, misafir.
- **Süper-admin** — kiracı/otel yönetimi (`admin/` panel).

## 3. Fonksiyonel Gereksinimler (FR)
- FR1 Oda & oda tipi yönetimi + müsaitlik.
- FR2 Rezervasyon (oluştur/iptal/taşı).
- FR3 Check-in / check-out.
- FR4 Misafir kayıtları.
- FR5 Raporlama (doluluk, gelir).
- FR6 Admin panel (kiracı/kullanıcı).

## 4. Fonksiyonel Olmayan Gereksinimler (NFR)
- NFR1 Güvenlik: JWT + bcrypt.
- NFR2 Kiracı izolasyonu.
- NFR3 Erişim: `otel.zk.net.tr` (Cloudflare Access arkasında).

## 5. Mimari (SDD)
```
app/ (FastAPI)
  routers/  — admin/ + hotel/ + public
  models/   — SQLAlchemy
  services/ — iş mantığı
  templates/{admin,hotel}/ — Jinja2
  static/
docker-compose.yml — otel (:8200→8000) + postgres:16
```

## 6. Açık İşler (ajan görevleri)
- [ ] Fiyatlandırma/kampanya kuralları.
- [ ] Kanal yöneticisi (OTA) entegrasyonu.
- [ ] AI asistan (InsightMap gateway) Phase 3.

## 7. Ortam
- Canlı: `otel.zk.net.tr`. Konteyner `otel` :8200.
