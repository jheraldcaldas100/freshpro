from datetime import timedelta
from unittest import mock

import pytest
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone

from catalogo.models import Carrera, Oportunidad
from tests.catalogo.conftest import csv_de, fila

pytestmark = pytest.mark.django_db
URL_HOJA = "https://docs.google.com/spreadsheets/d/e/2PACX-abc/pub?gid=0&single=true&output=csv"
IMPORTAR = "admin:catalogo_oportunidad_importar"


@pytest.fixture
def contenido_cliente(client):
    usuario = User.objects.create_user("contenido", password="clave-segura-123", is_staff=True)
    usuario.groups.add(Group.objects.get(name="Contenido"))
    client.force_login(usuario)
    return client


@pytest.fixture
def con_hoja(settings):
    settings.HOJA_CSV_URL = URL_HOJA


def test_grupo_contenido_ve_catalogo_y_no_usuarios(contenido_cliente):
    indice = contenido_cliente.get(reverse("admin:index")).content.decode()
    assert "Oportunidades" in indice and "Carreras" in indice
    assert "Usuarios" not in indice and "Grupos" not in indice
    assert contenido_cliente.get(reverse("admin:auth_user_changelist")).status_code == 403


def test_grupo_contenido_no_puede_borrar(contenido_cliente, crear_oportunidad):
    oportunidad = crear_oportunidad(todas_carreras=True)
    url = reverse("admin:catalogo_oportunidad_delete", args=[oportunidad.pk])
    assert contenido_cliente.get(url).status_code == 403


def _datos_formulario(**cambios):
    datos = {
        "codigo": "BEC-2026-050",
        "titulo": "Beca",
        "organizacion": "Org",
        "tipo": "beca",
        "ciclo_min": 1,
        "ciclo_max": 12,
        "fecha_cierre": (timezone.localdate() + timedelta(days=20)).isoformat(),
        "resumen_1": "a",
        "resumen_2": "b",
        "resumen_3": "c",
        "requisitos": "r",
        "link_postulacion": "https://example.com/a",
        "fuente_url": "https://example.com/b",
        "frecuencia": "anual",
        "estado": "borrador",
    }
    datos.update(cambios)
    return datos


def test_formulario_carreras_o_todas(contenido_cliente):
    agregar = reverse("admin:catalogo_oportunidad_add")
    economia = Carrera.objects.get(nombre="Economía").pk
    ninguna = contenido_cliente.post(agregar, _datos_formulario())
    assert "Elige al menos una carrera" in ninguna.content.decode()
    ambas = contenido_cliente.post(
        agregar, _datos_formulario(todas_carreras="on", carreras=[economia])
    )
    assert "no ambas" in ambas.content.decode()
    contenido_cliente.post(agregar, _datos_formulario(carreras=[economia]))
    oportunidad = Oportunidad.objects.get(codigo="BEC-2026-050")
    cambiar = reverse("admin:catalogo_oportunidad_change", args=[oportunidad.pk])
    contenido_cliente.post(cambiar, _datos_formulario(todas_carreras="on"))
    oportunidad.refresh_from_db()
    assert oportunidad.todas_carreras and not oportunidad.carreras.exists()
    contenido_cliente.post(cambiar, _datos_formulario(carreras=[economia]))
    oportunidad.refresh_from_db()
    assert not oportunidad.todas_carreras and oportunidad.carreras.count() == 1


@pytest.mark.parametrize(
    "cambio",
    [
        {"fecha_cierre": (timezone.localdate() + timedelta(days=40)).isoformat()},
        {"hora_cierre": "12:00"},
        {"link_postulacion": "https://example.com/otro"},
        {"fuente_url": "https://example.com/otra"},
    ],
)
def test_editar_campo_sensible_en_admin_invalida(contenido_cliente, crear_oportunidad, cambio):
    oportunidad = crear_oportunidad(
        codigo="BEC-2026-050",
        todas_carreras=True,
        verificado_at=timezone.now(),
        estado="publicada",
        fecha_cierre=timezone.localdate() + timedelta(days=20),
    )
    url = reverse("admin:catalogo_oportunidad_change", args=[oportunidad.pk])
    respuesta = contenido_cliente.post(
        url, _datos_formulario(todas_carreras="on", estado="publicada", **cambio), follow=True
    )
    oportunidad.refresh_from_db()
    assert oportunidad.estado == "borrador" and oportunidad.verificado_at is None
    assert "requerir verificación" in respuesta.content.decode()


def test_editar_titulo_no_invalida(contenido_cliente, crear_oportunidad):
    oportunidad = crear_oportunidad(
        codigo="BEC-2026-050",
        todas_carreras=True,
        verificado_at=timezone.now(),
        estado="publicada",
        fecha_cierre=timezone.localdate() + timedelta(days=20),
    )
    url = reverse("admin:catalogo_oportunidad_change", args=[oportunidad.pk])
    contenido_cliente.post(
        url, _datos_formulario(todas_carreras="on", estado="publicada", titulo="Otro título")
    )
    oportunidad.refresh_from_db()
    assert oportunidad.titulo == "Otro título" and oportunidad.estado == "publicada"


@pytest.mark.parametrize("nombre", ["economia", "  ECONOMÍA  "])
def test_carrera_equivalente_en_formulario_admin(contenido_cliente, nombre):
    respuesta = contenido_cliente.post(reverse("admin:catalogo_carrera_add"), {"nombre": nombre})
    assert respuesta.status_code == 200
    assert "se considera el mismo nombre" in respuesta.content.decode()
    finanzas = Carrera.objects.get(nombre="Finanzas")
    renombrar = contenido_cliente.post(
        reverse("admin:catalogo_carrera_change", args=[finanzas.pk]), {"nombre": nombre}
    )
    assert "se considera el mismo nombre" in renombrar.content.decode()


def test_acciones_publicar_y_verificar(contenido_cliente, crear_oportunidad):
    a = crear_oportunidad(codigo="A-1", todas_carreras=True)
    b = crear_oportunidad(codigo="B-1", todas_carreras=True, verificado_at=timezone.now())
    url = reverse("admin:catalogo_oportunidad_changelist")
    contenido_cliente.post(url, {"action": "publicar", "_selected_action": [a.pk, b.pk]})
    a.refresh_from_db(), b.refresh_from_db()
    assert a.estado == "borrador" and b.estado == "publicada"
    contenido_cliente.post(url, {"action": "marcar_verificada", "_selected_action": [a.pk]})
    a.refresh_from_db()
    assert a.verificado_at is not None


def test_filtros_de_cierre_y_verificacion(contenido_cliente, crear_oportunidad):
    hoy = timezone.localdate()
    crear_oportunidad(codigo="PRONTO", todas_carreras=True, fecha_cierre=hoy + timedelta(days=3))
    crear_oportunidad(
        codigo="LEJOS",
        todas_carreras=True,
        fecha_cierre=hoy + timedelta(days=60),
        verificado_at=timezone.now(),
    )
    crear_oportunidad(codigo="VENCIDA", todas_carreras=True, fecha_cierre=hoy - timedelta(days=1))
    url = reverse("admin:catalogo_oportunidad_changelist")
    pronto = contenido_cliente.get(url, {"cierre": "7"}).content.decode()
    assert "PRONTO" in pronto and "LEJOS" not in pronto and "VENCIDA" not in pronto
    vencida = contenido_cliente.get(url, {"cierre": "vencida"}).content.decode()
    assert "VENCIDA" in vencida and "PRONTO" not in vencida
    sin_verificar = contenido_cliente.get(url, {"verificacion": "vencida"}).content.decode()
    assert "PRONTO" in sin_verificar and "LEJOS" not in sin_verificar


def _sincronizar(cliente, contenido):
    with mock.patch("catalogo.origen_hoja.descargar", return_value=contenido):
        return cliente.post(reverse(IMPORTAR), {"accion": "hoja"})


def test_sincronizar_vista_previa_y_confirmar(contenido_cliente, con_hoja):
    vista = _sincronizar(contenido_cliente, csv_de([fila()]))
    assert "Se crearán" in vista.content.decode()
    assert Oportunidad.objects.count() == 0
    identificador = vista.context["id_pendiente"]
    contenido_cliente.post(reverse(IMPORTAR), {"accion": "confirmar", "id": identificador})
    assert Oportunidad.objects.filter(codigo="BEC-2026-001").exists()
    assert "catalogo_importacion_pendiente" not in contenido_cliente.session


def test_confirma_lo_previsualizado_aunque_la_hoja_cambie(contenido_cliente, con_hoja):
    vista = _sincronizar(contenido_cliente, csv_de([fila()]))
    with mock.patch(
        "catalogo.origen_hoja.descargar", return_value=csv_de([fila(titulo="Cambiado")])
    ):
        contenido_cliente.post(
            reverse(IMPORTAR), {"accion": "confirmar", "id": vista.context["id_pendiente"]}
        )
    assert Oportunidad.objects.get().titulo == "Beca de prueba"


def test_vista_previa_obsoleta_es_rechazada(contenido_cliente, con_hoja):
    primera = _sincronizar(contenido_cliente, csv_de([fila()]))
    _sincronizar(contenido_cliente, csv_de([fila(codigo="OTRA-1")]))
    respuesta = contenido_cliente.post(
        reverse(IMPORTAR),
        {"accion": "confirmar", "id": primera.context["id_pendiente"]},
        follow=True,
    )
    assert "ya no es válida" in respuesta.content.decode()
    assert Oportunidad.objects.count() == 0


def test_sincronizacion_fallida_descarta_la_pendiente(contenido_cliente, con_hoja):
    from catalogo.origen_hoja import ErrorHoja

    primera = _sincronizar(contenido_cliente, csv_de([fila()]))
    with mock.patch("catalogo.origen_hoja.descargar", side_effect=ErrorHoja("caída")):
        contenido_cliente.post(reverse(IMPORTAR), {"accion": "hoja"})
    contenido_cliente.post(
        reverse(IMPORTAR), {"accion": "confirmar", "id": primera.context["id_pendiente"]}
    )
    assert Oportunidad.objects.count() == 0


def test_confirmar_sin_pendiente(contenido_cliente):
    respuesta = contenido_cliente.post(
        reverse(IMPORTAR), {"accion": "confirmar", "id": "x"}, follow=True
    )
    assert "ya no es válida" in respuesta.content.decode()


def test_vista_previa_con_errores_no_permite_confirmar(contenido_cliente, con_hoja):
    vista = _sincronizar(contenido_cliente, csv_de([fila(tipo="x")]))
    contenido = vista.content.decode()
    assert "No se importará nada" in contenido and "Confirmar importación" not in contenido
    assert "catalogo_importacion_pendiente" not in contenido_cliente.session


def test_hoja_sin_configurar(contenido_cliente, settings):
    settings.HOJA_CSV_URL = ""
    pagina = contenido_cliente.get(reverse(IMPORTAR)).content.decode()
    assert "La hoja no está configurada" in pagina


def test_subir_csv(contenido_cliente):
    from django.core.files.uploadedfile import SimpleUploadedFile

    archivo = SimpleUploadedFile("c.csv", csv_de([fila()]), content_type="text/csv")
    vista = contenido_cliente.post(reverse(IMPORTAR), {"accion": "subir", "archivo": archivo})
    assert "Se crearán" in vista.content.decode()


def test_usuario_sin_permiso_recibe_403(client):
    usuario = User.objects.create_user("solo-staff", password="x-clave-segura", is_staff=True)
    client.force_login(usuario)
    assert client.get(reverse(IMPORTAR)).status_code == 403


def test_lista_muestra_boton_importar_solo_con_permiso(contenido_cliente, client):
    lista = reverse("admin:catalogo_oportunidad_changelist")
    assert reverse(IMPORTAR) in contenido_cliente.get(lista).content.decode()
    solo_ver = User.objects.create_user("lector", password="x-clave-segura", is_staff=True)
    solo_ver.user_permissions.add(
        *Group.objects.get(name="Contenido").permissions.filter(codename__startswith="view_")
    )
    client.force_login(solo_ver)
    assert reverse(IMPORTAR) not in client.get(lista).content.decode()
