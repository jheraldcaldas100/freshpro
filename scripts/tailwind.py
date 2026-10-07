"""Compila assets/app.css -> static/css/app.css con el CLI standalone de Tailwind.

Descarga el binario de la versión fijada para tu sistema operativo en bin/ (una sola vez).
No necesita Node. Uso:

    uv run python scripts/tailwind.py           # compila una vez
    uv run python scripts/tailwind.py --watch   # recompila al guardar plantillas

Si no puedes descargar desde GitHub, define TAILWIND_BIN con la ruta a un binario
o comando equivalente de la misma versión.
"""

import os
import platform
import shlex
import stat
import subprocess
import sys
import urllib.request
from pathlib import Path

VERSION = "4.3.3"
RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "assets" / "app.css"
SALIDA = RAIZ / "static" / "css" / "app.css"


def nombre_binario() -> str:
    sistema = {"Linux": "linux", "Darwin": "macos", "Windows": "windows"}.get(platform.system())
    maquina = platform.machine().lower()
    arquitectura = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64", "aarch64": "arm64"}.get(
        maquina
    )
    if not sistema or not arquitectura:
        sys.exit(f"Sistema no soportado: {platform.system()} {platform.machine()}")
    extension = ".exe" if sistema == "windows" else ""
    return f"tailwindcss-{sistema}-{arquitectura}{extension}"


def obtener_binario() -> list[str]:
    if comando := os.environ.get("TAILWIND_BIN"):
        return shlex.split(comando)
    nombre = nombre_binario()
    destino = RAIZ / "bin" / f"{VERSION}-{nombre}"
    if not destino.exists():
        url = f"https://github.com/tailwindlabs/tailwindcss/releases/download/v{VERSION}/{nombre}"
        print(f"Descargando Tailwind {VERSION} ({nombre})...")
        destino.parent.mkdir(exist_ok=True)
        temporal = destino.with_suffix(".descarga")
        urllib.request.urlretrieve(url, temporal)
        temporal.replace(destino)
        destino.chmod(destino.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return [str(destino)]


def main() -> None:
    comando = [*obtener_binario(), "-i", str(ENTRADA), "-o", str(SALIDA), "--minify"]
    if "--watch" in sys.argv[1:]:
        comando.append("--watch")
    subprocess.run(comando, check=True, cwd=RAIZ)


if __name__ == "__main__":
    main()
