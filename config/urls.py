from django.conf import settings
from django.contrib import admin
from django.urls import path

from core.views import InicioView

admin.site.site_header = "Oppu · Administración"
admin.site.site_title = "Oppu"
admin.site.index_title = "Panel de contenido"

urlpatterns = [
    path("", InicioView.as_view(), name="inicio"),
    path(settings.ADMIN_URL, admin.site.urls),
]
