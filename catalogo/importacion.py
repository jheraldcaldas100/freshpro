"""Importación de convocatorias desde un CSV (archivo subido o hoja publicada).

Todo o nada: si alguna fila tiene errores, no se importa ninguna.
La hoja manda en el contenido; `estado` y `verificado_at` los maneja el admin.
"""

import csv
import io
from dataclasses import dataclass, field
from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction

from .models import CICLO_MAX, CICLO_MIN, Carrera, Interes, Oportunidad
from .normalizacion import normalizar
from .validacion import errores_de_carreras, invalidar_si_cambio_sensible, valores_sensibles

TAMANO_MAXIMO = 2 * 1024 * 1024

COLUMNAS = [
    "codigo",
    "titulo",
    "organizacion",
    "tipo",
    "carreras",
    "intereses",
    "ciclo_min",
    "ciclo_max",
    "fecha_apertura",
    "fecha_cierre",
    "hora_cierre",
    "resumen_1",
    "resumen_2",
    "resumen_3",
    "requisitos",
    "link_postulacion",
    "fuente_url",
    "frecuencia",
]

CAMPOS_SIMPLES = [
    "titulo",
    "organizacion",
    "tipo",
    "todas_carreras",
    "ciclo_min",
    "ciclo_max",
    "fecha_apertura",
    "fecha_cierre",
    "hora_cierre",
    "resumen_1",
    "resumen_2",
    "resumen_3",
    "requisitos",
    "link_postulacion",
    "fuente_url",
    "frecuencia",
]

SINONIMOS_TIPO = {
    "beca": "beca",
    "becas": "beca",
    "practicas": "practicas",
    "practica": "practicas",
    "practicas y empleo": "practicas",
    "empleo": "practicas",
    "intercambio": "intercambio",
    "doble grado": "doble_grado",
    "concurso": "concurso",
    "taller": "taller",
    "voluntariado": "voluntariado",
}
SINONIMOS_FRECUENCIA = {"unica": "unica", "anual": "anual", "recurrente": "recurrente"}
FORMATOS_FECHA = ("%d/%m/%Y", "%Y-%m-%d")
LONGITUD_MAXIMA = {
    "titulo": 120,
    "organizacion": 120,
    "resumen_1": 120,
    "resumen_2": 120,
    "resumen_3": 120,
}
OBLIGATORIOS = ["titulo", "organizacion", "resumen_1", "resumen_2", "resumen_3", "requisitos"]


@dataclass
class FilaValida:
    numero: int
    codigo: str
    campos: dict
    carreras: list
    intereses: list


@dataclass
class Reporte:
    errores_generales: list[str] = field(default_factory=list)
    errores: list[str] = field(default_factory=list)
    creadas: list[str] = field(default_factory=list)
    actualizadas: list[str] = field(default_factory=list)
    reverificar: list[str] = field(default_factory=list)
    sin_cambios: list[str] = field(default_factory=list)
    no_presentes: list[str] = field(default_factory=list)
    aplicado: bool = False

    @property
    def ok(self) -> bool:
        return not self.errores_generales and not self.errores

    @property
    def total_filas(self) -> int:
        return len(self.creadas) + len(self.actualizadas) + len(self.sin_cambios)


def _clave_tipo(valor: str) -> str:
    return normalizar(valor.replace("_", " "))


def _leer(contenido: bytes, reporte: Reporte) -> list[tuple[int, dict]]:
    if len(contenido) > TAMANO_MAXIMO:
        reporte.errores_generales.append("El archivo pesa más de 2 MB.")
        return []
    try:
        texto = contenido.decode("utf-8-sig")
    except UnicodeDecodeError:
        reporte.errores_generales.append(
            "El archivo no está en UTF-8. Expórtalo desde Google Sheets como CSV."
        )
        return []
    lector = csv.reader(io.StringIO(texto, newline=""))
    try:
        encabezados = [normalizar(h).replace(" ", "_") for h in next(lector)]
    except StopIteration:
        reporte.errores_generales.append("El archivo está vacío.")
        return []
    repetidos = sorted({h for h in encabezados if encabezados.count(h) > 1})
    faltantes = [c for c in COLUMNAS if c not in encabezados]
    sobrantes = [h for h in encabezados if h and h not in COLUMNAS]
    if repetidos:
        reporte.errores_generales.append(f"Columnas repetidas: {', '.join(repetidos)}.")
    if faltantes:
        reporte.errores_generales.append(f"Faltan columnas: {', '.join(faltantes)}.")
    if sobrantes:
        reporte.errores_generales.append(
            f"Columnas no previstas: {', '.join(sobrantes)}. "
            "(estado y verificación se manejan en el admin, no en la hoja)."
        )
    if reporte.errores_generales:
        return []
    filas = []
    for numero, celdas in enumerate(lector, start=2):
        if not any(c.strip() for c in celdas):
            continue
        if len(celdas) != len(encabezados):
            reporte.errores.append(
                f"Fila {numero}: tiene {len(celdas)} celdas y se esperaban {len(encabezados)}."
            )
            continue
        filas.append((numero, dict(zip(encabezados, (c.strip() for c in celdas), strict=True))))
    if not filas and not reporte.errores:
        reporte.errores_generales.append("El archivo no tiene filas con datos.")
    return filas


def _fecha(valor: str) -> date:
    for formato in FORMATOS_FECHA:
        try:
            return datetime.strptime(valor, formato).date()
        except ValueError:
            continue
    raise ValueError


def _validar_fila(numero: int, fila: dict, catalogos: dict) -> tuple[FilaValida | None, list]:
    codigo = fila["codigo"].upper()
    etiqueta = f"Fila {numero} ({codigo or 'sin código'})"
    errores: list[str] = []
    campos: dict = {}

    def error(campo: str, mensaje: str) -> None:
        errores.append(f"{etiqueta}: {campo}: {mensaje}")

    if not codigo:
        error("codigo", "es obligatorio.")
    for campo in OBLIGATORIOS:
        if not fila[campo]:
            error(campo, "es obligatorio.")
        elif len(fila[campo]) > LONGITUD_MAXIMA.get(campo, 10_000):
            error(campo, f"tiene más de {LONGITUD_MAXIMA[campo]} caracteres.")
        else:
            campos[campo] = fila[campo]

    tipo = SINONIMOS_TIPO.get(_clave_tipo(fila["tipo"]))
    if tipo:
        campos["tipo"] = tipo
    else:
        error("tipo", f'"{fila["tipo"]}" no es válido. Usa: {", ".join(Oportunidad.Tipo.values)}.')
    frecuencia = SINONIMOS_FRECUENCIA.get(normalizar(fila["frecuencia"]))
    if frecuencia:
        campos["frecuencia"] = frecuencia
    else:
        error("frecuencia", f'"{fila["frecuencia"]}" no es válida. Usa: unica, anual, recurrente.')

    for campo in ("ciclo_min", "ciclo_max"):
        try:
            ciclo = int(fila[campo])
            if not CICLO_MIN <= ciclo <= CICLO_MAX:
                raise ValueError
            campos[campo] = ciclo
        except ValueError:
            error(campo, f'"{fila[campo]}" debe ser un número de {CICLO_MIN} a {CICLO_MAX}.')

    for campo, obligatorio in (("fecha_apertura", False), ("fecha_cierre", True)):
        if not fila[campo]:
            if obligatorio:
                error(campo, "es obligatoria.")
            else:
                campos[campo] = None
            continue
        try:
            campos[campo] = _fecha(fila[campo])
        except ValueError:
            error(campo, f'"{fila[campo]}" no es una fecha válida (usa DD/MM/AAAA).')
    if fila["hora_cierre"]:
        try:
            campos["hora_cierre"] = datetime.strptime(fila["hora_cierre"], "%H:%M").time()
        except ValueError:
            error("hora_cierre", f'"{fila["hora_cierre"]}" no es una hora válida (usa HH:MM).')
    else:
        campos["hora_cierre"] = None

    validar_url = URLValidator(schemes=["https"])
    for campo in ("link_postulacion", "fuente_url"):
        try:
            validar_url(fila[campo])
            campos[campo] = fila[campo]
        except ValidationError:
            error(campo, f'"{fila[campo]}" debe ser una URL que empiece con https://.')

    nombres_carreras = [n.strip() for n in fila["carreras"].split(";") if n.strip()]
    todas = [normalizar(n) for n in nombres_carreras] == ["todas"]
    campos["todas_carreras"] = todas
    carreras = []
    if not todas:
        for nombre in nombres_carreras:
            if normalizar(nombre) == "todas":
                error("carreras", '"todas" no se puede combinar con carreras específicas.')
            elif carrera := catalogos["carreras"].get(normalizar(nombre)):
                carreras.append(carrera)
            else:
                error(
                    "carreras", f'"{nombre}" no existe. Válidas: {catalogos["nombres_carreras"]}.'
                )
        for mensaje in errores_de_carreras(nombres_carreras, todas):
            error("carreras", mensaje)
    intereses = []
    for nombre in (n.strip() for n in fila["intereses"].split(";") if n.strip()):
        if interes := catalogos["intereses"].get(normalizar(nombre)):
            intereses.append(interes)
        else:
            error("intereses", f'"{nombre}" no existe. Válidos: {catalogos["nombres_intereses"]}.')

    if not errores:
        provisional = Oportunidad(codigo=codigo, **campos)
        try:
            provisional.full_clean(exclude=["codigo"], validate_unique=False)
        except ValidationError as exc:
            for campo, mensajes in exc.message_dict.items():
                for mensaje in mensajes:
                    error(campo, mensaje)
    if errores:
        return None, errores
    return FilaValida(numero, codigo, campos, carreras, intereses), []


def _catalogos() -> dict:
    carreras = {c.clave: c for c in Carrera.objects.all()}
    intereses = {i.clave: i for i in Interes.objects.all()}
    return {
        "carreras": carreras,
        "intereses": intereses,
        "nombres_carreras": ", ".join(c.nombre for c in carreras.values()) or "(ninguna)",
        "nombres_intereses": ", ".join(i.nombre for i in intereses.values()) or "(ninguno)",
    }


def _sin_cambios(oportunidad: Oportunidad, fila: FilaValida) -> bool:
    if any(getattr(oportunidad, c) != fila.campos[c] for c in CAMPOS_SIMPLES):
        return False
    carreras = {c.pk for c in oportunidad.carreras.all()}
    intereses = {i.pk for i in oportunidad.intereses.all()}
    return carreras == {c.pk for c in fila.carreras} and intereses == {i.pk for i in fila.intereses}


def importar(contenido: bytes, confirmar: bool = False) -> Reporte:
    """Valida el CSV y, si `confirmar` y no hay errores, lo aplica en una transacción."""
    reporte = Reporte()
    filas = _leer(contenido, reporte)
    if reporte.errores_generales:
        return reporte

    catalogos = _catalogos()
    validas: list[FilaValida] = []
    lineas_por_codigo: dict[str, list[int]] = {}
    for numero, fila in filas:
        valida, errores = _validar_fila(numero, fila, catalogos)
        reporte.errores.extend(errores)
        codigo = fila["codigo"].upper()
        if codigo:
            lineas_por_codigo.setdefault(codigo, []).append(numero)
        if valida:
            validas.append(valida)
    for codigo, lineas in lineas_por_codigo.items():
        if len(lineas) > 1:
            reporte.errores.append(
                f"El código {codigo} se repite en las filas {', '.join(map(str, lineas))}."
            )
    if not reporte.ok:
        return reporte

    existentes = {
        o.codigo: o
        for o in Oportunidad.objects.filter(
            codigo__in=[f.codigo for f in validas]
        ).prefetch_related("carreras", "intereses")
    }
    presentes = {f.codigo for f in validas}
    reporte.no_presentes = list(
        Oportunidad.objects.exclude(codigo__in=presentes)
        .order_by("codigo")
        .values_list("codigo", flat=True)
    )

    with transaction.atomic():
        for fila in validas:
            oportunidad = existentes.get(fila.codigo)
            if oportunidad is None:
                reporte.creadas.append(fila.codigo)
                if confirmar:
                    nueva = Oportunidad.objects.create(codigo=fila.codigo, **fila.campos)
                    nueva.carreras.set(fila.carreras)
                    nueva.intereses.set(fila.intereses)
                continue
            if _sin_cambios(oportunidad, fila):
                reporte.sin_cambios.append(fila.codigo)
                continue
            anteriores = valores_sensibles(oportunidad)
            for campo, valor in fila.campos.items():
                setattr(oportunidad, campo, valor)
            reporte.actualizadas.append(fila.codigo)
            if invalidar_si_cambio_sensible(oportunidad, anteriores):
                reporte.reverificar.append(fila.codigo)
            if confirmar:
                oportunidad.save()
                oportunidad.carreras.set(fila.carreras)
                oportunidad.intereses.set(fila.intereses)
    reporte.aplicado = confirmar
    return reporte
