# Desarrollo de Oppu

## Requisitos

- **uv** (gestiona Python y dependencias): <https://docs.astral.sh/uv/getting-started/installation/>
  - Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git**.

No hace falta instalar Python a mano (uv instala la versión 3.12 del proyecto) ni Node.

## Levantar el proyecto en local

```bash
git clone https://github.com/jheraldcaldas100/freshpro.git
cd freshpro
uv sync                                  # instala Python 3.12 y las dependencias
uv run python manage.py migrate          # crea la base local (SQLite, db.sqlite3)
uv run python manage.py runserver
```

Abre <http://127.0.0.1:8000/> (inicio) y <http://127.0.0.1:8000/salud/> (debe decir `{"estado": "ok"}`).

Al arrancar, la consola muestra qué base de datos se está usando, por ejemplo `[oppu] Base de datos: sqlite3 (...)`.

Para entrar al admin (<http://127.0.0.1:8000/admin/>):

```bash
uv run python manage.py createsuperuser
```

### Usar PostgreSQL en local (opcional)

Copia `.env.example` como `.env` y define `DATABASE_URL`. El entorno de desarrollo lee `.env` automáticamente; una variable ya definida en la terminal tiene prioridad.

## Estilos (Tailwind)

La fuente es `assets/app.css`; el resultado compilado `static/css/app.css` **se versiona**. Si cambias clases en las plantillas:

```bash
uv run python scripts/tailwind.py           # compila una vez
uv run python scripts/tailwind.py --watch   # recompila al guardar
```

La primera vez descarga el CLI de Tailwind (versión fijada) en `bin/`. Haz commit del `static/css/app.css` actualizado: CI falla si no coincide con las plantillas.

## Calidad

```bash
uv run ruff check .          # lint
uv run ruff format .         # formato
uv run pytest                # pruebas
```

CI (GitHub Actions) ejecuta además las pruebas en PostgreSQL 16, el chequeo de seguridad de producción, la verificación del CSS y la construcción de la imagen Docker. Ver `.github/workflows/ci.yml`.

## Configuración por entorno

| Variable | Desarrollo | Producción |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` (por defecto) | `config.settings.prod` |
| `SECRET_KEY` | opcional | **obligatoria** |
| `DATABASE_URL` | opcional (SQLite por defecto) | **obligatoria** (Neon) |
| `ALLOWED_HOSTS` | no se usa | dominios extra; Render agrega el suyo solo |
| `CSRF_TRUSTED_ORIGINS` | no se usa | `https://` + dominios extra |
| `ADMIN_URL` | `admin/` | **obligatoria**, ruta no obvia (no se acepta `admin/`) |
| `HOJA_CSV_URL` | opcional | link de la hoja publicada como CSV (ver "Contenido") |

Producción **nunca** lee `.env`.

## Despliegue: Render + Neon

### 1. Base de datos en Neon

1. Crea una cuenta en <https://neon.tech> y un proyecto (región más cercana: `AWS São Paulo` si está disponible, si no `US East`).
2. Copia la **connection string** (formato `postgresql://...?sslmode=require`). Esa es la `DATABASE_URL`.

### 2. Servicio web en Render

1. Crea una cuenta en <https://render.com> con GitHub y autoriza el repositorio.
2. **New → Blueprint** y elige este repositorio: Render lee `render.yaml` y crea el servicio `oppu` (Docker, plan gratuito, health check en `/salud/`, `SECRET_KEY` generada automáticamente).
3. Completa las variables que pide:
   - `DATABASE_URL`: la de Neon.
   - `ADMIN_URL`: una ruta difícil de adivinar, por ejemplo `gestion-` + 6 caracteres al azar + `/`. Guárdala en un lugar seguro del equipo.
4. Despliega. Al terminar, abre `https://<servicio>.onrender.com/salud/`.

En el plan gratuito el servicio se **duerme** tras ~15 minutos sin uso y tarda ~1 minuto en despertar. Antes de las entrevistas (F6) se pasa a un plan pagado.

### 3. Crear el superusuario (Render gratis no tiene consola)

Desde tu máquina, contra la base de Neon:

```bash
# macOS / Linux
DJANGO_SETTINGS_MODULE=config.settings.prod SECRET_KEY=temporal ALLOWED_HOSTS=localhost \
ADMIN_URL=temporal/ DATABASE_URL="<la de Neon>" uv run python manage.py createsuperuser
```

```powershell
# Windows (PowerShell)
$env:DJANGO_SETTINGS_MODULE="config.settings.prod"; $env:SECRET_KEY="temporal"; $env:ALLOWED_HOSTS="localhost"
$env:ADMIN_URL="temporal/"; $env:DATABASE_URL="<la de Neon>"
uv run python manage.py createsuperuser
```

Usa una contraseña fuerte. Cierra la terminal al terminar para no dejar esas variables cargadas. Las migraciones las aplica el propio servicio al arrancar, así que hazlo **después** del primer despliegue.

## Contenido: hoja → admin

### Preparar la hoja (una sola vez)

1. Crea una Google Sheet con una cuenta Gmail del equipo (algunas cuentas universitarias no permiten "Publicar en la web").
2. Archivo → Importar → sube `datos/plantilla_convocatorias.csv` → "Reemplazar hoja actual". Borra las filas `EJEMPLO-1` y `EJEMPLO-2` cuando cargues convocatorias reales.
3. Validación de datos (Datos → Validación de datos) en la columna `tipo` (beca, practicas, intercambio, doble_grado, concurso, taller, voluntariado) y en `frecuencia` (unica, anual, recurrente).
4. Para notas internas usa **otra pestaña**: la de convocatorias será pública para quien tenga el link.
5. **Publicar:** Archivo → Compartir → Publicar en la web → elige **solo la pestaña de convocatorias** y el formato **Valores separados por comas (.csv)** → Publicar. En "Contenido publicado y configuración", **activa "Volver a publicar automáticamente cuando se realicen cambios"**.
6. Copia el link (empieza con `https://docs.google.com/spreadsheets/d/e/` y termina en `output=csv`) y cárgalo en Render como variable `HOJA_CSV_URL` (Environment → Add Environment Variable). Render redespliega solo.

### Flujo diario

1. Edita la hoja siguiendo `docs/reglas-etiquetado.md`.
2. En el admin: Oportunidades → **Importar / sincronizar** → **Sincronizar desde la hoja**.
3. Revisa la vista previa. Si hay errores, corrígelos en la hoja y vuelve a sincronizar. Si no ves un cambio reciente, espera 5 minutos (Google tarda en actualizar el CSV publicado).
4. **Confirmar importación.** Las nuevas entran como borrador.
5. En la lista, selecciona las que revisaste → acción **Marcar como verificada ahora** → luego **Publicar**.

Volver a sincronizar nunca despublica. Pero si cambias la fecha de cierre, la hora o un link, esa convocatoria vuelve a borrador y hay que verificarla de nuevo.

**Respaldo:** si la sincronización falla, Archivo → Descargar → CSV y usa **Subir un CSV** en la misma pantalla. Desde la terminal: `uv run python manage.py importar_convocatorias archivo.csv --dry-run` (o `--hoja`).

### Usuario para la persona de contenido

En el admin (con un superusuario): Usuarios → Agregar usuario → marca **Es staff** y agrégalo al grupo **Contenido**. No le marques "Es superusuario". Ese grupo puede ver, crear y editar convocatorias, carreras e intereses, pero no borrar ni gestionar usuarios.

## Estructura

```
config/        settings (base, dev, prod), urls, wsgi
core/          página de inicio y /salud/
catalogo/ perfiles/ feed/ entrevistas/ eventos/   apps del producto (se llenan desde F1)
templates/     plantillas
assets/        fuente de Tailwind
static/        estáticos publicados (CSS compilado)
scripts/       tailwind.py, start.sh
tests/         pruebas
analisis/      notebooks de análisis (desde F4)
docs/          plan, fases y esta guía
```
