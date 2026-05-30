# Deployment — My Online Market

Production stack: **Docker Compose** (PostgreSQL + Redis + Django/Gunicorn +
Celery + Next.js + Nginx). Target: AWS EC2 (Ubuntu) yoki har qanday Docker
host.

---

## 1. Talablar

- Docker 24+ va Docker Compose v2
- Domen (ixtiyoriy) + SSL uchun (Let's Encrypt)
- Cloudinary akkaunt (media), Upstash/Redis, SMTP (email)

## 2. Server tayyorlash (Ubuntu EC2)

```bash
# Docker o'rnatish
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER && newgrp docker

# Repo
git clone https://github.com/Javohir263/my-online-market.git
cd my-online-market
```

## 3. Environment

**backend/.env** (production):
```ini
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<kuchli-tasodifiy-kalit>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DJANGO_CORS_ALLOWED_ORIGINS=https://yourdomain.com

# DB / cache (compose ichida override qilinadi)
DATABASE_URL=postgres://mom:STRONG_PASS@postgres:5432/mom
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Cloudinary
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Email
DJANGO_EMAIL_BACKEND=anymail.backends.mailgun.EmailBackend
MAILGUN_API_KEY=...
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Sentry (ixtiyoriy)
SENTRY_DSN=...

# SMS (Eskiz)
ESKIZ_EMAIL=...
ESKIZ_PASSWORD=...
```

**Root .env** (compose o'zgaruvchilari):
```ini
POSTGRES_USER=mom
POSTGRES_PASSWORD=STRONG_PASS
POSTGRES_DB=mom
NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1
NEXT_PUBLIC_SITE_URL=https://yourdomain.com
```

## 4. Ishga tushirish

```bash
docker compose -f docker-compose.prod.yml up -d --build

# Superuser yaratish
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Admin theme + (ixtiyoriy) demo data
docker compose -f docker-compose.prod.yml exec backend python manage.py seed_admin_theme
docker compose -f docker-compose.prod.yml exec backend python manage.py seed_demo
```

Sayt: `http://<server-ip>/` · Admin: `http://<server-ip>/admin/`

## 5. HTTPS (Let's Encrypt)

Nginx oldiga `certbot` yoki `nginx-proxy + acme-companion` qo'shing, yoki
Caddy reverse-proxy. So'ng `nginx/nginx.conf` ga 443 server bloki + SSL
sertifikat yo'llarini qo'shing va `DJANGO_DEBUG=False` da
`SECURE_SSL_REDIRECT=True` allaqachon yoqilgan.

## 6. Yangilash

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

## 7. Monitoring

- `docker compose -f docker-compose.prod.yml logs -f backend`
- Sentry (errors), `/health/` (uptime)
- Celery: `docker compose ... logs -f celery`

---

## Alternativa — split deploy

- **Frontend → Vercel** (Next.js native): `frontend/` ni Vercel'ga ulang,
  `NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1`.
- **Backend → EC2/Render**: `backend/` Docker yoki gunicorn + nginx.
- CORS/CSRF `DJANGO_*` env'larida frontend domenini qo'shing.
