"""Descarga del CSV de una Google Sheet publicada en la web ("Publicar en la web" → CSV).

La URL viene solo de la variable de entorno HOJA_CSV_URL. Cada redirección se valida
antes de pedirla, la lectura se corta a los 2 MB y toda la descarga tiene 15 s en total.
"""

import http.client
import time
from collections.abc import Callable
from typing import Protocol
from urllib.parse import parse_qs, urljoin, urlsplit

from django.conf import settings

from .importacion import TAMANO_MAXIMO

HOST_HOJA = "docs.google.com"
SUFIJO_CONTENIDO = ".googleusercontent.com"
PRESUPUESTO_SEGUNDOS = 15.0
MAX_REDIRECCIONES = 3
BLOQUE = 64 * 1024
CODIGOS_REDIRECCION = {301, 302, 303, 307, 308}


class ErrorHoja(Exception):
    """Error comprensible para mostrar a la persona de contenido."""


class Respuesta(Protocol):
    status: int

    def getheader(self, nombre: str, default: str | None = None) -> str | None: ...

    def read(self, cantidad: int, tiempo_restante: float) -> bytes: ...

    def close(self) -> None: ...


Transporte = Callable[[str, float], Respuesta]


def url_permitida(url: str) -> bool:
    partes = urlsplit(url)
    if partes.scheme != "https" or partes.username or partes.password:
        return False
    if partes.port not in (None, 443):
        return False
    host = (partes.hostname or "").lower()
    return host == HOST_HOJA or host.endswith(SUFIJO_CONTENIDO)


def es_url_de_hoja_publicada(url: str) -> bool:
    if not url_permitida(url):
        return False
    partes = urlsplit(url)
    return (
        (partes.hostname or "").lower() == HOST_HOJA
        and partes.path.startswith("/spreadsheets/d/e/")
        and parse_qs(partes.query).get("output") == ["csv"]
    )


def url_configurada() -> str | None:
    url = getattr(settings, "HOJA_CSV_URL", "")
    return url if url and es_url_de_hoja_publicada(url) else None


class RespuestaHttps:
    """Respuesta de http.client cuyo tiempo de espera se ajusta en cada lectura."""

    def __init__(self, conexion: http.client.HTTPSConnection):
        self._conexion = conexion
        self._respuesta = conexion.getresponse()
        self.status = self._respuesta.status

    def getheader(self, nombre: str, default: str | None = None) -> str | None:
        return self._respuesta.getheader(nombre, default)

    def read(self, cantidad: int, tiempo_restante: float) -> bytes:
        if self._conexion.sock is not None:
            self._conexion.sock.settimeout(tiempo_restante)
        return self._respuesta.read(cantidad)

    def close(self) -> None:
        self._respuesta.close()
        self._conexion.close()


def transporte_https(url: str, tiempo_restante: float) -> Respuesta:
    partes = urlsplit(url)
    conexion = http.client.HTTPSConnection(partes.hostname, timeout=tiempo_restante)
    ruta = partes.path or "/"
    if partes.query:
        ruta += f"?{partes.query}"
    conexion.request("GET", ruta, headers={"User-Agent": "Oppu/1.0"})
    return RespuestaHttps(conexion)


def descargar(
    url: str,
    transporte: Transporte = transporte_https,
    reloj: Callable[[], float] = time.monotonic,
) -> bytes:
    limite = reloj() + PRESUPUESTO_SEGUNDOS

    def restante() -> float:
        segundos = limite - reloj()
        if segundos <= 0:
            raise ErrorHoja("La hoja tardó más de 15 segundos en responder. Intenta de nuevo.")
        return segundos

    actual = url
    for _ in range(MAX_REDIRECCIONES + 1):
        if not url_permitida(actual):
            raise ErrorHoja("La hoja redirigió a una dirección no permitida. Revisa el link.")
        try:
            respuesta = transporte(actual, restante())
        except ErrorHoja:
            raise
        except (OSError, http.client.HTTPException) as exc:
            raise ErrorHoja(f"No se pudo conectar con Google Sheets ({exc}).") from exc
        try:
            if respuesta.status in CODIGOS_REDIRECCION:
                destino = respuesta.getheader("Location")
                if not destino:
                    raise ErrorHoja("Google respondió una redirección sin destino.")
                actual = urljoin(actual, destino)
                continue
            if respuesta.status != 200:
                raise ErrorHoja(f"Google Sheets respondió con el error {respuesta.status}.")
            tipo = (respuesta.getheader("Content-Type") or "").lower()
            if "html" in tipo:
                raise ErrorHoja(
                    "Google devolvió una página web en vez del CSV: la hoja no está publicada "
                    "o el link no es el de 'Publicar en la web' en formato CSV."
                )
            if "csv" not in tipo and "text/plain" not in tipo:
                raise ErrorHoja(f"Google devolvió un tipo de contenido inesperado ({tipo}).")
            return _leer_con_limites(respuesta, restante)
        finally:
            respuesta.close()
    raise ErrorHoja("Demasiadas redirecciones al descargar la hoja.")


def _leer_con_limites(respuesta: Respuesta, restante: Callable[[], float]) -> bytes:
    partes: list[bytes] = []
    total = 0
    while True:
        try:
            bloque = respuesta.read(BLOQUE, restante())
        except (OSError, http.client.HTTPException) as exc:
            raise ErrorHoja(f"Se cortó la descarga de la hoja ({exc}).") from exc
        if not bloque:
            return b"".join(partes)
        total += len(bloque)
        if total > TAMANO_MAXIMO:
            raise ErrorHoja("La hoja pesa más de 2 MB.")
        partes.append(bloque)
