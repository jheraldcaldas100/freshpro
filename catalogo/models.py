from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from .normalizacion import normalizar

ZONA_LIMA = ZoneInfo("America/Lima")
DIAS_VIGENCIA_VERIFICACION = 7
TOLERANCIA_FUTURO = timedelta(minutes=5)
CICLO_MIN, CICLO_MAX = 1, 12


def validar_https(valor: str) -> None:
    if not valor.lower().startswith("https://"):
        raise ValidationError("La URL debe empezar con https://")


class CatalogoBase(models.Model):
    nombre = models.CharField(max_length=80)
    clave = models.CharField(max_length=80, unique=True, editable=False)

    class Meta:
        abstract = True
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre

    def save(self, *args, **kwargs):
        self.clave = normalizar(self.nombre)
        super().save(*args, **kwargs)

    def clean(self) -> None:
        self.nombre = " ".join(self.nombre.split())
        self.clave = normalizar(self.nombre)
        if not self.clave:
            raise ValidationError({"nombre": "El nombre no puede estar vacío."})
        repetido = type(self).objects.filter(clave=self.clave).exclude(pk=self.pk).first()
        if repetido:
            raise ValidationError(
                {"nombre": f'Ya existe "{repetido.nombre}", que se considera el mismo nombre.'}
            )


class Carrera(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "carrera"
        verbose_name_plural = "carreras"


class Interes(CatalogoBase):
    class Meta(CatalogoBase.Meta):
        verbose_name = "interés"
        verbose_name_plural = "intereses"


class Oportunidad(models.Model):
    class Tipo(models.TextChoices):
        BECA = "beca", "Beca"
        PRACTICAS = "practicas", "Prácticas y empleo"
        INTERCAMBIO = "intercambio", "Intercambio"
        DOBLE_GRADO = "doble_grado", "Doble grado"
        CONCURSO = "concurso", "Concurso"
        TALLER = "taller", "Taller"
        VOLUNTARIADO = "voluntariado", "Voluntariado"

    class Frecuencia(models.TextChoices):
        UNICA = "unica", "Única"
        ANUAL = "anual", "Anual"
        RECURRENTE = "recurrente", "Recurrente"

    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        PUBLICADA = "publicada", "Publicada"
        CERRADA = "cerrada", "Cerrada"

    codigo = models.CharField(
        "código",
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(r"^[A-Za-z0-9-]+$", "Solo letras, números y guiones (sin espacios).")
        ],
        help_text="Identificador estable, p. ej. BEC-2026-014. Es la llave de la importación.",
    )
    titulo = models.CharField("título", max_length=120)
    organizacion = models.CharField("organización", max_length=120)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    carreras = models.ManyToManyField(Carrera, blank=True, related_name="oportunidades")
    todas_carreras = models.BooleanField("todas las carreras", default=False)
    intereses = models.ManyToManyField(Interes, blank=True, related_name="oportunidades")
    ciclo_min = models.PositiveSmallIntegerField(
        "ciclo mínimo", validators=[MinValueValidator(CICLO_MIN), MaxValueValidator(CICLO_MAX)]
    )
    ciclo_max = models.PositiveSmallIntegerField(
        "ciclo máximo", validators=[MinValueValidator(CICLO_MIN), MaxValueValidator(CICLO_MAX)]
    )
    fecha_apertura = models.DateField("fecha de apertura", null=True, blank=True)
    fecha_cierre = models.DateField("fecha de cierre")
    hora_cierre = models.TimeField(
        "hora de cierre", null=True, blank=True, help_text="Vacía = 23:59 de Lima."
    )
    resumen_1 = models.CharField("resumen 1", max_length=120)
    resumen_2 = models.CharField("resumen 2", max_length=120)
    resumen_3 = models.CharField("resumen 3", max_length=120)
    requisitos = models.TextField()
    link_postulacion = models.URLField(
        "link de postulación", max_length=500, validators=[validar_https]
    )
    fuente_url = models.URLField("fuente", max_length=500, validators=[validar_https])
    frecuencia = models.CharField(max_length=20, choices=Frecuencia.choices)
    verificado_at = models.DateTimeField("verificada el", null=True, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    creado_at = models.DateTimeField(auto_now_add=True)
    actualizado_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "oportunidad"
        verbose_name_plural = "oportunidades"
        ordering = ["fecha_cierre", "codigo"]
        constraints = [
            models.CheckConstraint(
                condition=Q(ciclo_min__lte=F("ciclo_max")), name="ciclo_min_lte_ciclo_max"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.codigo} · {self.titulo}"

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.strip().upper()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        # Se normaliza aquí (antes de validar unicidad) para que "bec-1" choque con "BEC-1"
        # como error de formulario y no como error de base de datos.
        self.codigo = (self.codigo or "").strip().upper()
        errores = {}
        if self.ciclo_min and self.ciclo_max and self.ciclo_min > self.ciclo_max:
            errores["ciclo_max"] = "El ciclo máximo no puede ser menor que el mínimo."
        if self.fecha_apertura and self.fecha_cierre and self.fecha_apertura > self.fecha_cierre:
            errores["fecha_apertura"] = "La apertura no puede ser posterior al cierre."
        if self.verificado_at and self.verificado_at > timezone.now() + TOLERANCIA_FUTURO:
            errores["verificado_at"] = "La verificación no puede estar en el futuro."
        if self.estado == self.Estado.PUBLICADA and not self.verificado_at:
            errores["estado"] = "Solo se puede publicar una oportunidad verificada."
        if errores:
            raise ValidationError(errores)

    @property
    def instante_cierre(self) -> datetime:
        return datetime.combine(
            self.fecha_cierre, self.hora_cierre or time(23, 59, 59), tzinfo=ZONA_LIMA
        )

    def dias_para_cierre(self, hoy=None) -> int:
        hoy = hoy or timezone.localdate()
        return (self.fecha_cierre - hoy).days

    def verificacion_vencida(self, ahora=None) -> bool:
        if not self.verificado_at:
            return True
        ahora = ahora or timezone.now()
        return ahora - self.verificado_at > timedelta(days=DIAS_VIGENCIA_VERIFICACION)
