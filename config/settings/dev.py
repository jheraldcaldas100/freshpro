"""Desarrollo local. Lee `.env` si existe; las variables ya definidas tienen prioridad."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(os.environ.get("OPPU_ENV_FILE", Path(__file__).resolve().parent.parent.parent / ".env"))

import dj_database_url  # noqa: E402

from .base import *  # noqa: E402, F403
from .base import BASE_DIR  # noqa: E402

DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "solo-para-desarrollo-no-usar-en-produccion")
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver"]

DATABASES = {
    "default": dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
}

if "runserver" in sys.argv:
    motor = DATABASES["default"]["ENGINE"].rsplit(".", 1)[-1]
    print(f"[oppu] Base de datos: {motor} ({DATABASES['default']['NAME']})", file=sys.stderr)
