import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from catalogo.models import Carrera, Interes

ESPERADOS = {
    f"{accion}_{modelo}"
    for modelo in ("oportunidad", "carrera", "interes")
    for accion in ("view", "add", "change")
}


def _permisos_contenido():
    return {p.codename for p in Group.objects.get(name="Contenido").permissions.all()}


@pytest.mark.django_db
def test_base_nueva_tiene_grupo_y_catalogos():
    assert _permisos_contenido() == ESPERADOS
    assert Carrera.objects.count() == 12
    assert Interes.objects.count() == 10


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_desde_f0_y_migrar_dos_veces():
    executor = MigrationExecutor(connection)
    executor.migrate([("catalogo", None)])  # estado de F0: catalogo sin migraciones
    Group.objects.filter(name="Contenido").delete()
    call_command("migrate", verbosity=0)
    call_command("migrate", verbosity=0)
    assert _permisos_contenido() == ESPERADOS
    assert Carrera.objects.count() == 12
