import importlib
from unittest import mock

import pytest
from django.db import DatabaseError
from django.test import override_settings
from django.urls import clear_url_caches

import config.urls

APPS_DEL_PRODUCTO = ["catalogo", "perfiles", "feed", "entrevistas", "eventos"]


def test_inicio(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert "core/inicio.html" in [t.name for t in respuesta.templates]
    assert "css/app.css" in respuesta.content.decode()


@pytest.mark.django_db
def test_salud_ok(client):
    respuesta = client.get("/salud/")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_salud_sin_bd(client):
    with mock.patch("core.middleware.connection.cursor", side_effect=DatabaseError("caída")):
        respuesta = client.get("/salud/")
    assert respuesta.status_code == 503
    assert respuesta.json()["estado"] == "error"


@pytest.mark.django_db
def test_admin_pide_login(client):
    respuesta = client.get("/admin/")
    assert respuesta.status_code == 302
    assert "/admin/login/" in respuesta.url


@pytest.fixture
def urls_con_admin(settings):
    def _recargar(ruta: str):
        settings.ADMIN_URL = ruta
        importlib.reload(config.urls)
        clear_url_caches()

    yield _recargar
    settings.ADMIN_URL = "admin/"
    importlib.reload(config.urls)
    clear_url_caches()


@pytest.mark.django_db
def test_admin_url_configurable(client, urls_con_admin):
    urls_con_admin("gestion-oppu/")
    assert client.get("/admin/").status_code == 404
    respuesta = client.get("/gestion-oppu/")
    assert respuesta.status_code == 302
    assert "/gestion-oppu/login/" in respuesta.url


def test_apps_registradas(settings):
    for app in APPS_DEL_PRODUCTO:
        assert app in settings.INSTALLED_APPS


@pytest.mark.django_db
def test_salud_por_http_no_redirige_y_raiz_si(client, cargar_settings):
    """Con la seguridad de prod, la sonda HTTP interna recibe 200 y el público va a HTTPS."""
    prod = cargar_settings(
        "config.settings.prod",
        {
            "SECRET_KEY": "x" * 60,
            "DATABASE_URL": "postgres://u:c@localhost/oppu",
            "ALLOWED_HOSTS": "oppu.example.com",
            "ADMIN_URL": "gestion-oppu/",
        },
    )
    with override_settings(
        ALLOWED_HOSTS=prod.ALLOWED_HOSTS,
        SECURE_SSL_REDIRECT=prod.SECURE_SSL_REDIRECT,
        SECURE_PROXY_SSL_HEADER=prod.SECURE_PROXY_SSL_HEADER,
    ):
        sonda = client.get("/salud/", HTTP_HOST="10.0.0.5:10000")
        publico = client.get("/", HTTP_HOST="oppu.example.com")
        host_ajeno = client.get("/", HTTP_HOST="otro.example.com")
    assert sonda.status_code == 200
    assert publico.status_code == 301
    assert publico.url.startswith("https://oppu.example.com/")
    assert host_ajeno.status_code == 400
