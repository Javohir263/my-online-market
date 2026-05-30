# My Online Market — Backend

Professional e-commerce marketplace (Uzum.uz uslubida) backend'i.

**Stack:** Django 5 · DRF · PostgreSQL 16 · Redis 7 · Celery · drf-spectacular · JWT-cookie auth · django-modeltranslation (uz/ru/en) · Cloudinary CDN · Eskiz SMS

---

## Loyiha tuzilishi

```
backend/
├── config/                 # Project root
│   ├── settings/
│   │   ├── base.py         # Umumiy konfiguratsiya (env'dan o'qiladi)
│   │   ├── development.py  # Dev override (DEBUG, debug-toolbar)
│   │   ├── production.py   # Prod override (HTTPS, HSTS, Sentry)
│   │   └── test.py         # Pytest override (eager Celery, locmem cache)
│   ├── celery.py           # Celery app
│   ├── urls.py             # Root URL conf (admin + /api/v1/ + /api/docs/)
│   ├── wsgi.py / asgi.py
├── apps/
│   ├── core/               # BaseModel, mixins, pagination, exceptions
│   ├── accounts/           # User, Address, OTP (B2)
│   ├── authn/              # JWT cookie auth (B3)
│   ├── vendors/            # Vendor model (B5)
│   ├── catalog/            # Category, Brand, Product, Variant (B5-B6)
│   ├── cart/, orders/, reviews/, wishlist/
│   ├── promotions/, payments/, notifications/
├── requirements/{base,development,production,test}.txt
├── manage.py
├── Dockerfile, docker-compose.yml, docker-compose.dev.yml
├── pyproject.toml          # Black + Ruff + Mypy + Pytest config
├── pytest.ini
├── .env.example
```

---

## Quick start (lokal)

### 1. Repo'ni klonlash va papka

```powershell
cd "C:\Najot ta'lim\loihalarim\my-online-market\backend"
```

### 2. Virtualenv va paketlar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements\development.txt
```

### 3. `.env` faylini sozlash

```powershell
Copy-Item .env.example .env
# .env'da DATABASE_URL, REDIS_URL, SECRET_KEY ni o'zingizning qiymatlaringiz bilan to'ldiring.
```

### 4. PostgreSQL + Redis ni ishga tushirish

**Variant A — Docker (tavsiya etiladi):**

```powershell
docker compose -f docker-compose.dev.yml up -d
```

**Variant B — lokal o'rnatish (Windows):**

- PostgreSQL: <https://www.postgresql.org/download/windows/> — `mom` foydalanuvchi va `mom` DB yarating
- Redis (Memurai): <https://www.memurai.com/get-memurai>

### 5. Migratsiyalar (B2 dan keyin)

```powershell
python manage.py migrate
python manage.py createsuperuser
```

### 6. Serverni ishga tushirish

```powershell
python manage.py runserver
```

- API root: <http://localhost:8000/api/v1/>
- OpenAPI schema: <http://localhost:8000/api/schema/>
- Swagger UI: <http://localhost:8000/api/docs/>
- ReDoc: <http://localhost:8000/api/redoc/>
- Django admin: <http://localhost:8000/admin/>
- Health: <http://localhost:8000/health/>

### 7. Celery (boshqa terminal)

```powershell
celery -A config worker --loglevel=info --pool=solo  # Windows uchun --pool=solo
celery -A config beat --loglevel=info
```

---

## Testlar

```powershell
pytest                    # barchasi
pytest -m "not slow"      # tez testlar
pytest --cov              # coverage bilan
```

---

## Lint / format

```powershell
black .
ruff check . --fix
mypy .
```

Yoki pre-commit hook (commit'dan oldin avtomatik):

```powershell
pre-commit install
```

---

## Settings split — qaysi'sini ishlatish?

Default — `config.settings.development` (manage.py ichida hardcoded).

Production'da `DJANGO_SETTINGS_MODULE=config.settings.production` env variable orqali override qilinadi (Dockerfile'da set qilingan).

| Muhit | Module | Foydalanish |
|---|---|---|
| Dev (manage.py runserver) | `config.settings.development` | Default |
| Production (Docker / EC2) | `config.settings.production` | Container ENV |
| Pytest | `config.settings.test` | `pytest.ini`'da set qilingan |

---

## API versiyasi va endpoint'lar

Barcha endpoint'lar `/api/v1/` ostida. Authentication — JWT in httpOnly cookies (B3 dan keyin).

`PROJECT-PLAN.md` da ~55 endpoint to'liq spetsifikatsiyasi mavjud.

---

## Roadmap

Plan'dagi B1-B17 bosqichlari. Hozirgi holat: **B1 (Backend skeleton) tugadi.**

Keyingisi → **B2 (Custom User + Accounts)**.
