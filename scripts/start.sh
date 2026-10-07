#!/bin/sh
# Arranque en producción. Migrar al iniciar es aceptable porque el demo corre con UNA instancia.
set -e
uv run --no-sync python manage.py migrate --noinput
exec uv run --no-sync gunicorn config.wsgi --bind "0.0.0.0:${PORT:-8000}" --workers 2 --access-logfile -
