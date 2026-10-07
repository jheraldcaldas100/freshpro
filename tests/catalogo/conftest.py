import csv
import io
from datetime import date, timedelta

import pytest
from django.utils import timezone

from catalogo.importacion import COLUMNAS
from catalogo.models import Carrera, Oportunidad


def fila(**cambios) -> dict:
    cierre = (timezone.localdate() + timedelta(days=30)).strftime("%d/%m/%Y")
    base = {
        "codigo": "BEC-2026-001",
        "titulo": "Beca de prueba",
        "organizacion": "Organización",
        "tipo": "beca",
        "carreras": "Economía;Finanzas",
        "intereses": "Investigación",
        "ciclo_min": "5",
        "ciclo_max": "10",
        "fecha_apertura": "",
        "fecha_cierre": cierre,
        "hora_cierre": "",
        "resumen_1": "Beneficio",
        "resumen_2": "Requisito",
        "resumen_3": "Plazo",
        "requisitos": "Promedio 14",
        "link_postulacion": "https://example.com/postular",
        "fuente_url": "https://example.com/fuente",
        "frecuencia": "anual",
    }
    base.update(cambios)
    return base


def csv_de(filas: list[dict], columnas=COLUMNAS, bom: bool = False) -> bytes:
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(columnas)
    for f in filas:
        escritor.writerow([f.get(c, "") for c in columnas])
    texto = salida.getvalue()
    return (("﻿" if bom else "") + texto).encode("utf-8")


@pytest.fixture
def crear_oportunidad(db):
    def _crear(**cambios) -> Oportunidad:
        datos = {
            "codigo": "BEC-2026-100",
            "titulo": "Beca",
            "organizacion": "Org",
            "tipo": "beca",
            "ciclo_min": 1,
            "ciclo_max": 12,
            "fecha_cierre": date.today() + timedelta(days=20),
            "resumen_1": "a",
            "resumen_2": "b",
            "resumen_3": "c",
            "requisitos": "r",
            "link_postulacion": "https://example.com/a",
            "fuente_url": "https://example.com/b",
            "frecuencia": "anual",
        }
        carreras = cambios.pop("carreras", None)
        datos.update(cambios)
        oportunidad = Oportunidad.objects.create(**datos)
        if carreras is not None:
            oportunidad.carreras.set(Carrera.objects.filter(nombre__in=carreras))
        return oportunidad

    return _crear
