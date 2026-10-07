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


@pytest.mark.parametrize(
    "url",
    [
        "https://docs.google.com:abc/spreadsheets/d/e/x/pub?output=csv",
        "https://[::1/spreadsheets/d/e/x/pub?output=csv",
    ],
)
def test_url_malformada_no_rompe(settings, url):
    settings.HOJA_CSV_URL = url
    assert origen_hoja.url_configurada() is None


def _servidor_lento(cabecera: bytes, goteo: bytes):
    """Servidor HTTP local: envía `cabecera` y luego `goteo` de a 1 byte cada 0,2 s."""
    import socket
    import threading
    import time

    servidor = socket.socket()
    servidor.bind(("127.0.0.1", 0))
    servidor.listen(1)
    detener = threading.Event()

    def atender():
        conexion, _ = servidor.accept()
        conexion.recv(4096)
        try:
            conexion.sendall(cabecera)
            for byte in goteo:
                if detener.is_set():
                    break
                conexion.sendall(bytes([byte]))
                time.sleep(0.2)
        except OSError:
            pass
        conexion.close()

    threading.Thread(target=atender, daemon=True).start()
    return servidor, detener


CABECERA_LARGO = b"HTTP/1.1 200 OK\r\nContent-Type: text/csv\r\nContent-Length: 1000\r\n\r\n"
CABECERA_CHUNKED = (
    b"HTTP/1.1 200 OK\r\nContent-Type: text/csv\r\nTransfer-Encoding: chunked\r\n\r\n1\r\nx\r\n"
)


@pytest.mark.parametrize(
    ("cabecera", "goteo"),
    [
        (CABECERA_LARGO, b"x" * 1000),
        # Fin de chunks y trailers que llegan muy lento: http.client los lee por dentro.
        (CABECERA_CHUNKED, b"0\r\nX-Trailer: " + b"y" * 200 + b"\r\n\r\n"),
    ],
)
def test_respuesta_real_lenta_respeta_el_presupuesto(cabecera, goteo):
    import http.client
    import time

    servidor, detener = _servidor_lento(cabecera, goteo)
    try:
        puerto = servidor.getsockname()[1]
        inicio = time.monotonic()
        limite = inicio + 1.0

        def restante():
            segundos = limite - time.monotonic()
            if segundos <= 0:
                raise ErrorHoja(origen_hoja.MENSAJE_TIEMPO)
            return segundos

        conexion = http.client.HTTPConnection("127.0.0.1", puerto, timeout=5)
        respuesta = origen_hoja.RespuestaHttps(conexion, restante(), "/")
        with pytest.raises(ErrorHoja, match="15 segundos"):
            origen_hoja._leer_con_limites(respuesta, restante)
        respuesta.close()
        assert time.monotonic() - inicio < 2.0
    finally:
        detener.set()
        servidor.close()


def test_url_no_ascii_no_rompe(settings):
    settings.HOJA_CSV_URL = "https://docs.google.com/spreadsheets/d/e/ñ/pub?output=csv"
    assert origen_hoja.url_configurada() is None
