# My Online Market

Premium e-commerce marketplace (Uzum.uz uslubida) — **Django 5 REST API** +
**Next.js 16** frontend. Uch tilli (uz/ru/en), JWT-cookie auth, to'liq
katalog · savat · buyurtma · sharh · promo · bildirishnoma oqimlari.

[![CI](https://github.com/Javohir263/my-online-market/actions/workflows/ci.yml/badge.svg)](https://github.com/Javohir263/my-online-market/actions/workflows/ci.yml)

---

## Tech stack

| Qatlam | Texnologiyalar |
|---|---|
| **Backend** | Django 5 · DRF · PostgreSQL 16 · Redis 7 · Celery · drf-spectacular · django-modeltranslation · Cloudinary · Argon2 |
| **Frontend** | Next.js 16 (App Router) · TypeScript · Tailwind v4 · shadcn/ui · TanStack Query · Zustand · React Hook Form + Zod · next-intl · framer-motion |
| **DevOps** | Docker Compose · Nginx · GitHub Actions CI · pytest (230) · Vitest |

## Monorepo tuzilishi

```
my-online-market/
├── backend/          # Django REST API
│   ├── apps/         # core, accounts, authn, vendors, catalog, cart,
│   │                 # orders, reviews, wishlist, promotions, payments,
│   │                 # notifications
│   ├── config/       # settings (base/development/production/test), celery
│   └── requirements/ # base / development / production / test
├── frontend/         # Next.js 16 storefront
│   └── src/
│       ├── app/[locale]/   # (storefront) + (auth) — uz/ru/en routing
│       ├── components/     # layout, product, cart, ui
│       ├── hooks/          # useCatalog, useCart, useAuth, useWishlist
│       ├── lib/api/        # axios client + server fetch + endpoints
│       └── messages/       # uz.json, ru.json, en.json
├── nginx/            # reverse proxy config
├── docker-compose.prod.yml
└── DEPLOYMENT.md
```

## Lokal ishga tushirish

### Backend
```bash
cd backend
python -m venv .venv && .venv\Scripts\Activate.ps1   # Windows
pip install -r requirements/development.txt -r requirements/test.txt
# .env'da DATABASE_URL (PostgreSQL) + REDIS_URL ni sozlang
python manage.py migrate
python manage.py seed_admin_theme       # admin brendi
python manage.py seed_demo              # demo katalog (picsum rasmlar)
python manage.py createsuperuser
python manage.py runserver              # :8000
```

### Frontend
```bash
cd frontend
npm install
# .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev                             # :3000 → /uz ga yo'naltiradi
```

### Celery (ixtiyoriy — async email)
```bash
cd backend
celery -A config worker -l info -P solo   # Windows
celery -A config beat -l info
```

## Testlar

```bash
# Backend — 230 test
cd backend && pytest

# Frontend — Vitest
cd frontend && npm run test:run
```

## API hujjati

Server ishga tushgach: **`http://localhost:8000/api/docs/`** (Swagger UI) ·
`/api/redoc/` · `/api/schema/` (OpenAPI).

## Asosiy endpoint guruhlari (`/api/v1/`)

`auth/` · `accounts/` · `catalog/` · `cart/` · `wishlist/` · `orders/` ·
`reviews/` · `promotions/` · `notifications/` · `i18n/`

## Deployment

To'liq ko'rsatma: [DEPLOYMENT.md](./DEPLOYMENT.md) — Docker Compose
(PostgreSQL + Redis + Gunicorn + Celery + Next.js + Nginx).

## Litsenziya

O'quv loyihasi — Najot ta'lim.
