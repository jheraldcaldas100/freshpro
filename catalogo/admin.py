import hashlib
import uuid
from datetime import timedelta

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from . import origen_hoja
from .forms import OportunidadAdminForm, SubirCsvForm
from .importacion import importar
from .models import DIAS_VIGENCIA_VERIFICACION, Carrera, Interes, Oportunidad
from .validacion import invalidar_si_cambio_sensible, valores_sensibles

CLAVE_SESION = "catalogo_importacion_pendiente"
AVISO_HOJA = (
    "La hoja de cálculo manda en el contenido: lo que cambies aquí (salvo estado y "
    "verificación) se sobrescribe en la próxima sincronización. Corrige también la hoja."
)


@admin.register(Carrera, Interes)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ["nombre"]
    search_fields = ["nombre"]


class CierreFilter(admin.SimpleListFilter):
    title = "cierre"
    parameter_name = "cierre"

    def lookups(self, request, model_admin):
        return [("7", "Cierra en ≤ 7 días"), ("14", "Cierra en ≤ 14 días"), ("vencida", "Vencidas")]

    def queryset(self, request, queryset):
        hoy = timezone.localdate()
        if self.value() in ("7", "14"):
            limite = hoy + timedelta(days=int(self.value()))
            return queryset.filter(fecha_cierre__gte=hoy, fecha_cierre__lte=limite)
        if self.value() == "vencida":
            return queryset.filter(fecha_cierre__lt=hoy)
        return queryset


class VerificacionFilter(admin.SimpleListFilter):
    title = "verificación"
    parameter_name = "verificacion"

    def lookups(self, request, model_admin):
        return [("vencida", "Vencida o ausente"), ("vigente", "Vigente")]

    def queryset(self, request, queryset):
        corte = timezone.now() - timedelta(days=DIAS_VIGENCIA_VERIFICACION)
        if self.value() == "vencida":
            return queryset.filter(verificado_at__isnull=True) | queryset.filter(
                verificado_at__lt=corte
            )
        if self.value() == "vigente":
            return queryset.filter(verificado_at__gte=corte)
        return queryset


@admin.register(Oportunidad)
class OportunidadAdmin(admin.ModelAdmin):
    form = OportunidadAdminForm
    change_list_template = "admin/catalogo/oportunidad/change_list.html"
    list_display = ["codigo", "titulo", "tipo", "cierre", "estado", "verificacion"]
    list_filter = [
        "tipo",
        "estado",
        "frecuencia",
        "carreras",
        CierreFilter,
        VerificacionFilter,
    ]
    search_fields = ["codigo", "titulo", "organizacion"]
    filter_horizontal = ["carreras", "intereses"]
    readonly_fields = ["verificado_at", "creado_at", "actualizado_at"]
    actions = ["marcar_verificada", "publicar", "cerrar"]
    fieldsets = [
        (None, {"fields": ["codigo", "titulo", "organizacion", "tipo"], "description": AVISO_HOJA}),
        (
            "A quién va dirigida",
            {"fields": ["todas_carreras", "carreras", "ciclo_min", "ciclo_max", "intereses"]},
        ),
        ("Fechas", {"fields": ["fecha_apertura", "fecha_cierre", "hora_cierre", "frecuencia"]}),
        ("Contenido", {"fields": ["resumen_1", "resumen_2", "resumen_3", "requisitos"]}),
        ("Links", {"fields": ["link_postulacion", "fuente_url"]}),
        ("Ciclo de vida", {"fields": ["estado", "verificado_at", "creado_at", "actualizado_at"]}),
    ]

    @admin.display(description="cierre", ordering="fecha_cierre")
    def cierre(self, obj):
        dias = obj.dias_para_cierre()
        fecha = obj.fecha_cierre.strftime("%d/%m/%Y")
        if dias < 0:
            return format_html('{} · <span style="color:#b91c1c">vencida</span>', fecha)
        return f"{fecha} · en {dias} días" if dias != 1 else f"{fecha} · mañana"

    @admin.display(description="verificación", ordering="verificado_at")
    def verificacion(self, obj):
        if not obj.verificado_at:
            return format_html('<span style="color:#b91c1c">{}</span>', "sin verificar")
        dias = (timezone.now() - obj.verificado_at).days
        texto = "hoy" if dias == 0 else f"hace {dias} días"
        if obj.verificacion_vencida():
            return format_html('<span style="color:#b91c1c">{}</span>', texto)
        return texto

    def save_model(self, request, obj, form, change):
        if change:
            anteriores = valores_sensibles(Oportunidad.objects.get(pk=obj.pk))
            if invalidar_si_cambio_sensible(obj, anteriores):
                messages.warning(
                    request,
                    f"{obj.codigo}: cambiaste la fecha de cierre o un link, así que vuelve a "
                    "requerir verificación (quedó como borrador).",
                )
        super().save_model(request, obj, form, change)

    @admin.action(description="Marcar como verificada ahora", permissions=["change"])
    def marcar_verificada(self, request, queryset):
        cantidad = queryset.update(verificado_at=timezone.now())
        messages.success(request, f"{cantidad} oportunidad(es) marcadas como verificadas.")

    @admin.action(description="Publicar", permissions=["change"])
    def publicar(self, request, queryset):
        sin_verificar = queryset.filter(verificado_at__isnull=True)
        rechazadas = list(sin_verificar.values_list("codigo", flat=True))
        cantidad = queryset.exclude(pk__in=sin_verificar).update(
            estado=Oportunidad.Estado.PUBLICADA
        )
        if cantidad:
            messages.success(request, f"{cantidad} oportunidad(es) publicadas.")
        if rechazadas:
            messages.warning(
                request, f"No se publicaron por no estar verificadas: {', '.join(rechazadas)}."
            )

    @admin.action(description="Pasar a cerrada", permissions=["change"])
    def cerrar(self, request, queryset):
        cantidad = queryset.update(estado=Oportunidad.Estado.CERRADA)
        messages.success(request, f"{cantidad} oportunidad(es) cerradas.")

    def puede_importar(self, request) -> bool:
        return self.has_add_permission(request) and self.has_change_permission(request)

    def changelist_view(self, request, extra_context=None):
        extra_context = {**(extra_context or {}), "puede_importar": self.puede_importar(request)}
        return super().changelist_view(request, extra_context=extra_context)

    # --- Importación -------------------------------------------------------------

    def get_urls(self):
        propias = [
            path(
                "importar/",
                self.admin_site.admin_view(self.vista_importar),
                name="catalogo_oportunidad_importar",
            )
        ]
        return propias + super().get_urls()

    def vista_importar(self, request):
        if not self.puede_importar(request):
            raise PermissionDenied
        contexto = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Importar convocatorias",
            "hoja_configurada": origen_hoja.url_configurada() is not None,
            "form_subir": SubirCsvForm(),
        }
        if request.method == "POST":
            accion = request.POST.get("accion")
            if accion == "confirmar":
                return self._confirmar(request)
            request.session.pop(CLAVE_SESION, None)
            contenido, origen = None, None
            if accion == "hoja":
                url = origen_hoja.url_configurada()
                if url is None:
                    messages.error(request, "La hoja no está configurada (HOJA_CSV_URL).")
                    return redirect(request.path)
                try:
                    contenido = origen_hoja.descargar(url)
                    origen = "hoja"
                except origen_hoja.ErrorHoja as exc:
                    messages.error(request, str(exc))
                    return redirect(request.path)
            elif accion == "subir":
                form = SubirCsvForm(request.POST, request.FILES)
                contexto["form_subir"] = form
                if form.is_valid():
                    contenido = form.cleaned_data["archivo"].read()
                    origen = "archivo"
            if contenido is not None:
                reporte = importar(contenido)
                contexto.update(reporte=reporte, origen=origen, descargado_at=timezone.now())
                if reporte.ok:
                    identificador = uuid.uuid4().hex
                    request.session[CLAVE_SESION] = {
                        "id": identificador,
                        "contenido": contenido.decode("utf-8-sig"),
                        "hash": hashlib.sha256(contenido).hexdigest(),
                        "origen": origen,
                    }
                    contexto["id_pendiente"] = identificador
        return TemplateResponse(request, "admin/catalogo/oportunidad/importar.html", contexto)

    def _confirmar(self, request):
        pendiente = request.session.get(CLAVE_SESION)
        if not pendiente or request.POST.get("id") != pendiente["id"]:
            messages.error(
                request,
                "Esta vista previa ya no es válida (se sincronizó otra vez o venció). "
                "Vuelve a sincronizar.",
            )
            return redirect(request.path)
        request.session.pop(CLAVE_SESION)
        contenido = pendiente["contenido"].encode("utf-8")
        reporte = importar(contenido, confirmar=True)
        if not reporte.ok:
            messages.error(request, "La importación tuvo errores y no se guardó nada.")
            return redirect(request.path)
        partes = [
            f"{len(reporte.creadas)} creadas",
            f"{len(reporte.actualizadas)} actualizadas",
            f"{len(reporte.sin_cambios)} sin cambios",
        ]
        messages.success(request, "Importación guardada: " + ", ".join(partes) + ".")
        if reporte.reverificar:
            messages.warning(
                request,
                "Requieren reverificación (cambió la fecha o un link): "
                + ", ".join(reporte.reverificar),
            )
        return redirect(reverse("admin:catalogo_oportunidad_changelist"))
