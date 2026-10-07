FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .

# Valores ficticios SOLO para este comando: no quedan en la imagen y no se conecta a la base.
RUN SECRET_KEY=build-only DATABASE_URL=sqlite:///:memory: ALLOWED_HOSTS=localhost \
    ADMIN_URL=build-only/ uv run --no-sync python manage.py collectstatic --noinput

RUN useradd --create-home --uid 1000 oppu && chown -R oppu /app
USER oppu

EXPOSE 8000
CMD ["sh", "scripts/start.sh"]
