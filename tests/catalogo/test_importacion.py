from datetime import timedelta
from pathlib import Path

import pytest
from django.core.management import call_command
from django.utils import timezone

from catalogo.importacion import COLUMNAS, importar
from catalogo.models import Oportunidad
from tests.catalogo.conftest import csv_de, fila

pytestmark = pytest.mark.django_db
PLANTILLA = Path(__file__).resolve().parents[2] / "datos" / "plantilla_convocatorias.csv"


def test_csv_valido_crea_oportunidades():
    contenido = csv_de([fila(), fila(codigo="PRA-2026-001", tipo="Prácticas", carreras="todas")])
    reporte = importar(contenido, confirmar=True)
    assert reporte.ok, reporte.errores
    assert sorted(reporte.creadas) == ["BEC-2026-001", "PRA-2026-001"]
    beca = Oportunidad.objects.get(codigo="BEC-2026-001")
    assert sorted(c.nombre for c in beca.carreras.all()) == ["Economía", "Finanzas"]
    assert [i.nombre for i in beca.intereses.all()] == ["Investigación"]
    assert beca.estado == Oportunidad.Estado.BORRADOR and beca.verificado_at is None
    practicas = Oportunidad.objects.get(codigo="PRA-2026-001")
    assert practicas.tipo == "practicas" and practicas.todas_carreras


def test_reimportar_igual_no_cambia_nada():
    contenido = csv_de([fila()])
    importar(contenido, confirmar=True)
    reporte = importar(contenido, confirmar=True)
    assert (reporte.creadas, reporte.actualizadas, reporte.sin_cambios) == (
        [],
        [],
        ["BEC-2026-001"],
    )


def test_cambio_de_titulo_y_carrera_actualiza_y_reemplaza_m2m():
    importar(csv_de([fila()]), confirmar=True)
    reporte = importar(csv_de([fila(titulo="Nuevo", carreras="Derecho")]), confirmar=True)
    assert reporte.actualizadas == ["BEC-2026-001"] and reporte.reverificar == []
    beca = Oportunidad.objects.get(codigo="BEC-2026-001")
    assert beca.titulo == "Nuevo"
    assert [c.nombre for c in beca.carreras.all()] == ["Derecho"]


@pytest.mark.parametrize(
    ("cambio", "fragmento"),
    [
        ({"fecha_cierre": "31/02/2026"}, "fecha_cierre"),
        ({"tipo": "pasantía"}, "tipo"),
        ({"carreras": "Medicina"}, "Medicina"),
        ({"ciclo_min": "0"}, "ciclo_min"),
        ({"link_postulacion": "http://example.com"}, "link_postulacion"),
        ({"carreras": "todas;Economía"}, "todas"),
        ({"carreras": ""}, "carreras"),
        ({"intereses": "Astronomía"}, "Astronomía"),
        ({"titulo": "x" * 121}, "titulo"),
        ({"hora_cierre": "25:00"}, "hora_cierre"),
    ],
)
def test_errores_por_fila_no_importan_nada(cambio, fragmento):
    reporte = importar(csv_de([fila(), fila(codigo="BEC-2026-002", **cambio)]), confirmar=True)
    assert not reporte.ok
    assert any("Fila 3 (BEC-2026-002)" in e and fragmento in e for e in reporte.errores)
    assert Oportunidad.objects.count() == 0


def test_varios_errores_se_reportan_todos():
    contenido = csv_de([fila(tipo="x"), fila(codigo="BEC-2026-002", ciclo_max="99")])
    reporte = importar(contenido)
    assert any("Fila 2" in e for e in reporte.errores)
    assert any("Fila 3" in e for e in reporte.errores)


def test_codigo_duplicado():
    reporte = importar(csv_de([fila(), fila(codigo="bec-2026-001")]))
    assert any("se repite en las filas 2, 3" in e for e in reporte.errores)


def test_columnas_faltantes_sobrantes_y_repetidas():
    columnas = [c for c in COLUMNAS if c != "frecuencia"] + ["estado", "titulo"]
    reporte = importar(csv_de([fila()], columnas=columnas))
    texto = " ".join(reporte.errores_generales)
    assert "frecuencia" in texto and "estado" in texto and "repetidas: titulo" in texto


def test_archivo_no_utf8_y_demasiado_grande():
    assert "UTF-8" in importar("codigo;título".encode("latin-1")).errores_generales[0]
    assert "2 MB" in importar(b"x" * (2 * 1024 * 1024 + 1)).errores_generales[0]


def test_fila_con_celdas_de_mas():
    contenido = csv_de([fila()]) + b"BEC-2026-009,extra" + b",x" * 30 + b"\n"
    reporte = importar(contenido)
    assert any("Fila 3: tiene" in e for e in reporte.errores)


def test_formatos_tolerados():
    iso = (timezone.localdate() + timedelta(days=10)).isoformat()
    contenido = csv_de(
        [
            fila(
                tipo="Doble grado",
                carreras="ECONOMIA; finanzas ",
                fecha_cierre=iso,
                frecuencia="Única",
            )
        ],
        bom=True,
    )
    reporte = importar(contenido, confirmar=True)
    assert reporte.ok, reporte.errores
    assert Oportunidad.objects.get().tipo == "doble_grado"


def test_recorrido_publicar_y_reimportar_no_despublica():
    contenido = csv_de([fila()])
    importar(contenido, confirmar=True)
    Oportunidad.objects.update(verificado_at=timezone.now(), estado="publicada")
    reporte = importar(contenido, confirmar=True)
    assert reporte.sin_cambios == ["BEC-2026-001"]
    beca = Oportunidad.objects.get()
    assert beca.estado == "publicada" and beca.verificado_at is not None


@pytest.mark.parametrize(
    "cambio",
    [
        {"fecha_cierre": (timezone.localdate() + timedelta(days=45)).strftime("%d/%m/%Y")},
        {"hora_cierre": "12:00"},
        {"link_postulacion": "https://example.com/otro"},
        {"fuente_url": "https://example.com/otra-fuente"},
    ],
)
def test_cambio_sensible_pide_reverificacion(cambio):
    importar(csv_de([fila()]), confirmar=True)
    Oportunidad.objects.update(verificado_at=timezone.now(), estado="publicada")
    reporte = importar(csv_de([fila(**cambio)]), confirmar=True)
    assert reporte.reverificar == ["BEC-2026-001"]
    beca = Oportunidad.objects.get()
    assert beca.estado == "borrador" and beca.verificado_at is None


def test_no_presentes_no_se_tocan(crear_oportunidad):
    crear_oportunidad(codigo="VIEJA-1", todas_carreras=True)
    reporte = importar(csv_de([fila()]), confirmar=True)
    assert reporte.no_presentes == ["VIEJA-1"]
    assert Oportunidad.objects.filter(codigo="VIEJA-1").exists()


def test_dry_run_no_escribe():
    reporte = importar(csv_de([fila()]))
    assert reporte.creadas == ["BEC-2026-001"] and not reporte.aplicado
    assert Oportunidad.objects.count() == 0


def test_plantilla_importa_sin_errores():
    reporte = importar(PLANTILLA.read_bytes())
    assert reporte.ok, reporte.errores_generales + reporte.errores
    assert reporte.creadas == ["EJEMPLO-1", "EJEMPLO-2"]


def test_comando(tmp_path, capsys):
    archivo = tmp_path / "c.csv"
    archivo.write_bytes(csv_de([fila()]))
    call_command("importar_convocatorias", str(archivo), "--dry-run")
    assert Oportunidad.objects.count() == 0
    call_command("importar_convocatorias", str(archivo))
    assert Oportunidad.objects.count() == 1
