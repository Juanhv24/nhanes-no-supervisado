"""Descarga los módulos de NHANES 2017-2018 en formato XPT a datos/crudos."""

import requests

from nhanes_no_supervisado.config import MODULOS, RUTA_CRUDOS, SUFIJO, URL_BASE

# Se emplea User-Agent para evitar que la petición sea rechazada
ENCABEZADOS = {"User-Agent": "Mozilla/5.0"}


def descargar_modulo(modulo: str) -> None:
    """Descarga un módulo si aún no existe en la carpeta de datos crudos."""
    nombre = f"{modulo}{SUFIJO}.xpt"
    destino = RUTA_CRUDOS / nombre

    if destino.exists():
        print(f"{nombre}: ya existe, se omite.")
        return

    url = f"{URL_BASE}/{nombre}"
    respuesta = requests.get(url, headers=ENCABEZADOS, timeout=60)
    # Un error HTTP detiene el script en lugar de guardar una página de error como .xpt
    respuesta.raise_for_status()

    destino.write_bytes(respuesta.content)
    print(f"{nombre}: descargado ({len(respuesta.content) / 1024:.0f} KB).")


def main() -> None:
    RUTA_CRUDOS.mkdir(parents=True, exist_ok=True)
    for modulo in MODULOS:
        descargar_modulo(modulo)


if __name__ == "__main__":
    main()
