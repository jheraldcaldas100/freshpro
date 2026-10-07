"""Producción. Nunca lee `.env`: todo viene de variables de entorno del hosting."""

import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import ADMIN_URL, lista_desde_entorno, variable_requerida

DEBUG = False
SECRET_KEY = variable_requerida("SECRET_KEY")
DATABASES = {
    "default": dj_database_url.parse(
        variable_requerida("DATABASE_URL"), conn_max_age=600, conn_health_checks=True
    ),
}

ALLOWED_HOSTS = lista_desde_entorno("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = lista_desde_entorno("CSRF_TRUSTED_ORIGINS")
# Render define esta variable con el dominio público del servicio.
if host_render := os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(host_render)
    CSRF_TRUSTED_ORIGINS.append(f"https://{host_render}")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("Falta la variable de entorno ALLOWED_HOSTS.")

if ADMIN_URL == "admin/":
    raise ImproperlyConfigured("En producción ADMIN_URL debe ser una ruta no obvia, no 'admin/'.")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# HSTS corto mientras dure el demo; se sube cuando el dominio sea definitivo.
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False
# Excepción deliberada: no se pide la lista de precarga de HSTS para un subdominio
# temporal de onrender.com; se revisa cuando haya dominio propio.
SILENCED_SYSTEM_CHECKS = ["security.W021"]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
