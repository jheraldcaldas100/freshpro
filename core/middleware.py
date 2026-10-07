from django.db import DatabaseError, connection
from django.http import JsonResponse

RUTA_SALUD = "/salud/"


def estado_salud() -> JsonResponse:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"estado": "error", "detalle": "base de datos"}, status=503)
    return JsonResponse({"estado": "ok"})


class SaludMiddleware:
    """Atiende /salud/ antes que el resto de middlewares.

    La sonda del hosting llega por HTTP interno y con un Host que no es el
    público: no debe pasar por la validación de ALLOWED_HOSTS ni por la
    redirección a HTTPS. La respuesta es fija y no expone datos.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == RUTA_SALUD and request.method in ("GET", "HEAD"):
            return estado_salud()
        return self.get_response(request)
