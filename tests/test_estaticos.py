from django.core.management import call_command
from django.test import override_settings

STORAGE_PROD = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}


def test_collectstatic_de_produccion(tmp_path):
    """Lo mismo que ejecuta el Dockerfile: si falla aquí, el despliegue falla."""
    with override_settings(STATIC_ROOT=tmp_path, STORAGES=STORAGE_PROD):
        call_command("collectstatic", interactive=False, verbosity=0)
    assert list((tmp_path / "css").glob("app.*.css"))
    assert (tmp_path / "staticfiles.json").exists()
