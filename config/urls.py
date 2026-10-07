from django.conf import settings
from django.contrib import admin
from django.urls import path

from core.views import InicioView

urlpatterns = [
    path("", InicioView.as_view(), name="inicio"),
    path(settings.ADMIN_URL, admin.site.urls),
]
