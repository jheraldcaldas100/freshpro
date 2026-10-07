from datetime import date, time, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from catalogo.models import ZONA_LIMA, Carrera, Oportunidad

pytestmark = pytest.mark.django_db


def test_ciclo_min_mayor_que_max_es_rechazado(crear_oportunidad):
    oportunidad = crear_oportunidad()
    oportunidad.ciclo_min, oportunidad.ciclo_max = 8, 5
    with pytest.raises(ValidationError) as exc:
        oportunidad.full_clean()
    assert "ciclo_max" in exc.value.message_dict


def test_restriccion_de_ciclos_en_la_base(crear_oportunidad):
    with pytest.raises(IntegrityError):
        crear_oportunidad(ciclo_min=9, ciclo_max=3)


def test_apertura_posterior_al_cierre(crear_oportunidad):
    oportunidad = crear_oportunidad()
    oportunidad.fecha_apertura = oportunidad.fecha_cierre + timedelta(days=1)
    with pytest.raises(ValidationError) as exc:
        oportunidad.full_clean()
    assert "fecha_apertura" in exc.value.message_dict


def test_url_sin_https(crear_oportunidad):
    oportunidad = crear_oportunidad()
    oportunidad.link_postulacion = "http://example.com"
    with pytest.raises(ValidationError) as exc:
        oportunidad.full_clean()
    assert "link_postulacion" in exc.value.message_dict


def test_publicada_requiere_verificacion(crear_oportunidad):
    oportunidad = crear_oportunidad(estado=Oportunidad.Estado.PUBLICADA)
    with pytest.raises(ValidationError) as exc:
        oportunidad.full_clean()
    assert "estado" in exc.value.message_dict


def test_verificacion_en_el_futuro(crear_oportunidad):
    oportunidad = crear_oportunidad()
    oportunidad.verificado_at = timezone.now() + timedelta(minutes=10)
    with pytest.raises(ValidationError) as exc:
        oportunidad.full_clean()
    assert "verificado_at" in exc.value.message_dict
    oportunidad.verificado_at = timezone.now() + timedelta(minutes=2)
    oportunidad.full_clean()


def test_instante_cierre(crear_oportunidad):
    oportunidad = crear_oportunidad(fecha_cierre=date(2027, 4, 30))
    assert oportunidad.instante_cierre == timezone.datetime(
        2027, 4, 30, 23, 59, 59, tzinfo=ZONA_LIMA
    )
    oportunidad.hora_cierre = time(18, 0)
    assert oportunidad.instante_cierre.hour == 18
    assert oportunidad.instante_cierre.tzinfo == ZONA_LIMA


def test_codigo_se_guarda_en_mayusculas(crear_oportunidad):
    assert crear_oportunidad(codigo="bec-2026-9").codigo == "BEC-2026-9"


def test_carrera_con_nombre_equivalente_es_rechazada():
    nueva = Carrera(nombre="  economia ")
    with pytest.raises(ValidationError) as exc:
        nueva.full_clean()
    assert "Economía" in str(exc.value)


def test_verificacion_vencida(crear_oportunidad):
    oportunidad = crear_oportunidad()
    assert oportunidad.verificacion_vencida()
    oportunidad.verificado_at = timezone.now() - timedelta(days=6)
    assert not oportunidad.verificacion_vencida()
    oportunidad.verificado_at = timezone.now() - timedelta(days=8)
    assert oportunidad.verificacion_vencida()
