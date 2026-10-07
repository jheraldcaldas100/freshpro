from django import forms

from .importacion import TAMANO_MAXIMO
from .models import Oportunidad
from .validacion import errores_de_carreras


class OportunidadAdminForm(forms.ModelForm):
    link_postulacion = forms.URLField(
        label="Link de postulación", max_length=500, assume_scheme="https"
    )
    fuente_url = forms.URLField(label="Fuente", max_length=500, assume_scheme="https")

    class Meta:
        model = Oportunidad
        fields = [
            "codigo",
            "titulo",
            "organizacion",
            "tipo",
            "todas_carreras",
            "carreras",
            "ciclo_min",
            "ciclo_max",
            "intereses",
            "fecha_apertura",
            "fecha_cierre",
            "hora_cierre",
            "frecuencia",
            "resumen_1",
            "resumen_2",
            "resumen_3",
            "requisitos",
            "link_postulacion",
            "fuente_url",
            "estado",
        ]

    def clean(self):
        datos = super().clean()
        for mensaje in errores_de_carreras(datos.get("carreras"), datos.get("todas_carreras")):
            self.add_error("carreras", mensaje)
        return datos


class SubirCsvForm(forms.Form):
    archivo = forms.FileField(label="Archivo CSV")

    def clean_archivo(self):
        archivo = self.cleaned_data["archivo"]
        if archivo.size > TAMANO_MAXIMO:
            raise forms.ValidationError("El archivo pesa más de 2 MB.")
        return archivo
