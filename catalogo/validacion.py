"""Reglas compartidas por el formulario del admin y la importación."""

from .models import Oportunidad

CAMPOS_SENSIBLES = ("fecha_cierre", "hora_cierre", "link_postulacion", "fuente_url")


def errores_de_carreras(carreras, todas_carreras: bool) -> list[str]:
    hay_carreras = bool(list(carreras or []))
    if todas_carreras and hay_carreras:
        return ['Marca "todas las carreras" o elige carreras específicas, no ambas.']
    if not todas_carreras and not hay_carreras:
        return ['Elige al menos una carrera o marca "todas las carreras".']
    return []


def valores_sensibles(oportunidad: Oportunidad) -> dict:
    return {campo: getattr(oportunidad, campo) for campo in CAMPOS_SENSIBLES}


def invalidar_si_cambio_sensible(oportunidad: Oportunidad, anteriores: dict) -> bool:
    """Si cambió fecha/hora de cierre o algún link, la verificación deja de valer.

    Borra `verificado_at` y, si estaba publicada, la devuelve a borrador.
    No guarda: devuelve True si hubo que invalidar.
    """
    cambio = any(getattr(oportunidad, c) != anteriores.get(c) for c in CAMPOS_SENSIBLES)
    if not cambio or (oportunidad.verificado_at is None and oportunidad.estado != "publicada"):
        return False
    oportunidad.verificado_at = None
    if oportunidad.estado == Oportunidad.Estado.PUBLICADA:
        oportunidad.estado = Oportunidad.Estado.BORRADOR
    return True
