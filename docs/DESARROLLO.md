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
