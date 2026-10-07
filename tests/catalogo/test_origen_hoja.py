import pytest

from catalogo import origen_hoja
from catalogo.origen_hoja import ErrorHoja, descargar

URL = "https://docs.google.com/spreadsheets/d/e/2PACX-abc/pub?gid=0&single=true&output=csv"
CONTENIDO = "https://doc-0s-1c-sheets.googleusercontent.com/pub/abc/def?output=csv"


class RespuestaFalsa:
    def __init__(
        self, status=200, headers=None, bloques=(b"a,b\n",), segundos_por_bloque=0.0, reloj=None
    ):
        self.status = status
        self._headers = {"Content-Type": "text/csv; charset=utf-8", **(headers or {})}
        self._bloques = list(bloques)
        self._segundos = segundos_por_bloque
        self._reloj = reloj
        self.cerrada = False

    def getheader(self, nombre, default=None):
        return self._headers.get(nombre, default)

    def read(self, cantidad, tiempo_restante):
        if self._reloj:
            self._reloj.avanzar(self._segundos)
        return self._bloques.pop(0) if self._bloques else b""

    def close(self):
        self.cerrada = True


class Reloj:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def avanzar(self, segundos):
        self.t += segundos


class Transporte:
    """Registra cada URL pedida y responde según un mapa url -> respuesta."""

    def __init__(self, respuestas, reloj=None, segundos_por_peticion=0.0):
        self.respuestas = respuestas
        self.pedidas = []
        self.reloj = reloj
        self.segundos = segundos_por_peticion

    def __call__(self, url, tiempo_restante):
        self.pedidas.append(url)
        if self.reloj:
            self.reloj.avanzar(self.segundos)
        return self.respuestas[url]


def redireccion(destino):
    return RespuestaFalsa(status=307, headers={"Location": destino, "Content-Type": "text/html"})


def test_cadena_permitida():
    transporte = Transporte({URL: redireccion(CONTENIDO), CONTENIDO: RespuestaFalsa()})
    assert descargar(URL, transporte=transporte) == b"a,b\n"
    assert transporte.pedidas == [URL, CONTENIDO]


@pytest.mark.parametrize(
    "destino",
    [
        "https://evil.example.com/x",
        "http://doc-0s.googleusercontent.com/x",
        "https://user@docs.google.com/x",
        "https://googleusercontent.com.ejemplo.org/x",
        "https://docs.google.com:8443/x",
    ],
)
def test_salto_no_permitido_no_se_pide(destino):
    transporte = Transporte({URL: redireccion(destino)})
    with pytest.raises(ErrorHoja, match="no permitida"):
        descargar(URL, transporte=transporte)
    assert transporte.pedidas == [URL]


def test_demasiadas_redirecciones():
    otra = "https://docs.google.com/otra"
    transporte = Transporte({URL: redireccion(otra), otra: redireccion(URL)})
    with pytest.raises(ErrorHoja, match="Demasiadas"):
        descargar(URL, transporte=transporte)
    assert len(transporte.pedidas) == 4


def test_corte_por_tamano_sin_content_length():
    bloques = [b"x" * (64 * 1024)] * 40
    transporte = Transporte({URL: RespuestaFalsa(bloques=bloques)})
    with pytest.raises(ErrorHoja, match="2 MB"):
        descargar(URL, transporte=transporte)


def test_presupuesto_total_de_tiempo():
    reloj = Reloj()
    lenta = RespuestaFalsa(bloques=[b"a"] * 10, segundos_por_bloque=3.0, reloj=reloj)
    transporte = Transporte(
        {URL: redireccion(CONTENIDO), CONTENIDO: lenta}, reloj=reloj, segundos_por_peticion=4.0
    )
    with pytest.raises(ErrorHoja, match="15 segundos"):
        descargar(URL, transporte=transporte, reloj=reloj)


def test_respuesta_html_y_error_http():
    html = RespuestaFalsa(headers={"Content-Type": "text/html"})
    with pytest.raises(ErrorHoja, match="no está publicada"):
        descargar(URL, transporte=Transporte({URL: html}))
    with pytest.raises(ErrorHoja, match="404"):
        descargar(URL, transporte=Transporte({URL: RespuestaFalsa(status=404)}))


def test_respuestas_se_cierran():
    primera, segunda = redireccion(CONTENIDO), RespuestaFalsa()
    descargar(URL, transporte=Transporte({URL: primera, CONTENIDO: segunda}))
    assert primera.cerrada and segunda.cerrada


@pytest.mark.parametrize(
    ("url", "valida"),
    [
        (URL, True),
        ("https://docs.google.com/spreadsheets/d/abc/edit", False),
        ("https://docs.google.com/spreadsheets/d/e/abc/pub?output=html", False),
        ("http://docs.google.com/spreadsheets/d/e/abc/pub?output=csv", False),
        ("https://example.com/spreadsheets/d/e/abc/pub?output=csv", False),
    ],
)
def test_url_configurada(settings, url, valida):
    settings.HOJA_CSV_URL = url
    assert (origen_hoja.url_configurada() is not None) is valida
