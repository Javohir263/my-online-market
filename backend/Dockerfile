# =============================================================================
# Multi-stage Dockerfile — production-ready, Python 3.12 slim
# =============================================================================

# ---------- Stage 1: builder ----------
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# OS deps for psycopg / Pillow / argon2
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
        gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ ./requirements/
RUN pip install --upgrade pip wheel \
    && pip wheel --wheel-dir=/wheels -r requirements/production.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PATH="/home/app/.local/bin:${PATH}"

# Runtime-only OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libjpeg62-turbo \
        gettext \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --create-home --gid app --shell /bin/bash app

WORKDIR /app

# Pre-built wheels'ni o'rnatish
COPY --from=builder /wheels /wheels
COPY requirements/ ./requirements/
RUN pip install --no-index --find-links=/wheels -r requirements/production.txt \
    && rm -rf /wheels

# Manba kod
COPY --chown=app:app . /app/

# Static + media papkalari
RUN mkdir -p /app/staticfiles /app/media \
    && chown -R app:app /app

USER app

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/health/ || exit 1

# Default: production WSGI server
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "60"]
