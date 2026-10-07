from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.management import create_contenttypes
from django.db import migrations

from catalogo.normalizacion import normalizar

# Carreras de pregrado de la Universidad del Pacífico (piloto). Editables en el admin.
CARRERAS = [
    "Administración",
    "Contabilidad",
    "Derecho",
    "Economía",
    "Finanzas",
    "Humanidades Digitales",
    "Ingeniería de la Información",
    "Ingeniería Empresarial",
    "Ingeniería en Innovación",
    "Marketing",
    "Negocios Internacionales",
    "Política, Filosofía y Economía",
]

INTERESES = [
    "Consultoría",
    "Finanzas",
    "Investigación",
    "Emprendimiento",
    "Tecnología",
    "Sector público",
    "Impacto social",
    "Marketing",
    "Derecho corporativo",
    "Idiomas",
]

GRUPO_CONTENIDO = "Contenido"
PERMISOS_CONTENIDO = [
    f"{accion}_{modelo}"
    for modelo in ("oportunidad", "carrera", "interes")
    for accion in ("view", "add", "change")
]


def crear_datos(apps, schema_editor):
    # Django crea tipos de contenido y permisos después de migrar (post_migrate):
    # se crean aquí explícitamente para poder asignarlos al grupo en esta misma migración.
    app_config = apps.get_app_config("catalogo")
    app_config.models_module = True
    create_contenttypes(app_config, apps=apps, verbosity=0)
    create_permissions(app_config, apps=apps, verbosity=0)

    Carrera = apps.get_model("catalogo", "Carrera")
    Interes = apps.get_model("catalogo", "Interes")
    for modelo, nombres in ((Carrera, CARRERAS), (Interes, INTERESES)):
        for nombre in nombres:
            modelo.objects.get_or_create(clave=normalizar(nombre), defaults={"nombre": nombre})

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    grupo, _ = Group.objects.get_or_create(name=GRUPO_CONTENIDO)
    permisos = Permission.objects.filter(
        content_type__app_label="catalogo", codename__in=PERMISOS_CONTENIDO
    )
    grupo.permissions.add(*permisos)


class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [migrations.RunPython(crear_datos, migrations.RunPython.noop)]
