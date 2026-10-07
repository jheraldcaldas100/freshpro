import importlib
import sys

import pytest

VARIABLES_PROD = {
    "SECRET_KEY": "clave-de-prueba-suficientemente-larga-para-pasar-check-deploy-1234567890",
    "DATABASE_URL": "postgres://usuario:clave@localhost:5432/oppu",
    "ALLOWED_HOSTS": "oppu.example.com",
    "CSRF_TRUSTED_ORIGINS": "https://oppu.example.com",
    "ADMIN_URL": "gestion-oppu/",
}


@pytest.fixture
def cargar_settings(monkeypatch):
    """Importa un módulo de settings desde cero con las variables dadas."""

    def _cargar(modulo: str, variables: dict[str, str]):
        for nombre in [*VARIABLES_PROD, "RENDER_EXTERNAL_HOSTNAME", "OPPU_ENV_FILE"]:
            monkeypatch.delenv(nombre, raising=False)
        for nombre, valor in variables.items():
            monkeypatch.setenv(nombre, valor)
        for nombre in [m for m in sys.modules if m.startswith("config.settings.")]:
            monkeypatch.delitem(sys.modules, nombre)
        return importlib.import_module(modulo)

    return _cargar
