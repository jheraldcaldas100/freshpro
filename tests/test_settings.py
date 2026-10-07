import pytest
from django.core.exceptions import ImproperlyConfigured

from tests.conftest import VARIABLES_PROD


@pytest.mark.parametrize("faltante", ["SECRET_KEY", "DATABASE_URL", "ALLOWED_HOSTS"])
def test_prod_exige_variables(cargar_settings, faltante):
    variables = {k: v for k, v in VARIABLES_PROD.items() if k != faltante}
    with pytest.raises(ImproperlyConfigured, match=faltante):
        cargar_settings("config.settings.prod", variables)


def test_prod_rechaza_admin_obvio(cargar_settings):
    with pytest.raises(ImproperlyConfigured, match="ADMIN_URL"):
        cargar_settings("config.settings.prod", {**VARIABLES_PROD, "ADMIN_URL": "admin"})


def test_prod_seguro(cargar_settings):
    prod = cargar_settings("config.settings.prod", VARIABLES_PROD)
    assert prod.DEBUG is False
    assert prod.SESSION_COOKIE_SECURE is True
    assert prod.CSRF_COOKIE_SECURE is True
    assert prod.SECURE_SSL_REDIRECT is True
    assert prod.SECURE_HSTS_SECONDS > 0
    assert prod.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


def test_prod_agrega_host_de_render(cargar_settings):
    prod = cargar_settings(
        "config.settings.prod",
        {**VARIABLES_PROD, "RENDER_EXTERNAL_HOSTNAME": "oppu.onrender.com"},
    )
    assert "oppu.onrender.com" in prod.ALLOWED_HOSTS
    assert "https://oppu.onrender.com" in prod.CSRF_TRUSTED_ORIGINS


def test_prod_no_lee_env(cargar_settings, tmp_path):
    archivo = tmp_path / ".env"
    archivo.write_text("SECRET_KEY=desde-archivo\n")
    variables = {k: v for k, v in VARIABLES_PROD.items() if k != "SECRET_KEY"}
    with pytest.raises(ImproperlyConfigured, match="SECRET_KEY"):
        cargar_settings("config.settings.prod", {**variables, "OPPU_ENV_FILE": str(archivo)})


def test_dev_carga_env(cargar_settings, tmp_path, monkeypatch):
    archivo = tmp_path / ".env"
    archivo.write_text("DATABASE_URL=postgres://u:c@db.local:5432/oppu_local\n")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    dev = cargar_settings("config.settings.dev", {"OPPU_ENV_FILE": str(archivo)})
    assert dev.DATABASES["default"]["HOST"] == "db.local"
    assert dev.DATABASES["default"]["NAME"] == "oppu_local"
