from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from catalogo import origen_hoja
from catalogo.importacion import importar


class Command(BaseCommand):
    help = "Importa convocatorias desde un CSV o desde la hoja publicada (HOJA_CSV_URL)."

    def add_arguments(self, parser):
        origen = parser.add_mutually_exclusive_group(required=True)
        origen.add_argument("archivo", nargs="?", help="Ruta al CSV.")
        origen.add_argument("--hoja", action="store_true", help="Descargar de HOJA_CSV_URL.")
        parser.add_argument("--dry-run", action="store_true", help="Validar sin guardar.")

    def handle(self, *args, archivo=None, hoja=False, dry_run=False, **opciones):
        if hoja:
            url = origen_hoja.url_configurada()
            if url is None:
                raise CommandError("HOJA_CSV_URL no está configurada o no es un link válido.")
            try:
                contenido = origen_hoja.descargar(url)
            except origen_hoja.ErrorHoja as exc:
                raise CommandError(str(exc)) from exc
        else:
            contenido = Path(archivo).read_bytes()
        reporte = importar(contenido, confirmar=not dry_run)
        for error in reporte.errores_generales + reporte.errores:
            self.stderr.write(error)
        if not reporte.ok:
            raise CommandError("Hay errores: no se importó nada.")
        verbo = "Se importarían" if dry_run else "Importadas"
        self.stdout.write(
            f"{verbo}: {len(reporte.creadas)} creadas, {len(reporte.actualizadas)} actualizadas "
            f"({len(reporte.reverificar)} requieren reverificación), "
            f"{len(reporte.sin_cambios)} sin cambios, {len(reporte.no_presentes)} no presentes."
        )
