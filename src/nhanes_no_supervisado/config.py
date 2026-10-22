"""Constantes del proyecto: semilla, parámetros de NHANES y rutas a la raíz del repositorio."""

from pathlib import Path

# Semilla única para toda función con azar
# (inicialización del GMM, remuestreo y prueba de estabilidad)
SEMILLA = 42

# Raíz del proyecto calculada desde la ubicación de este archivo.
# config.py -> nhanes_no_supervisado/ (0) -> src/ (1) -> raíz (2)
RAIZ = Path(__file__).resolve().parents[2]

RUTA_CRUDOS = RAIZ / "datos" / "crudos"
RUTA_PROCESADOS = RAIZ / "datos" / "procesados"
RUTA_INFORMES = RAIZ / "informes"

ARCHIVO_DEPURADO = RUTA_PROCESADOS / "nhanes_depurado.parquet"

# Ciclo de NHANES y sufijo que la CDC asigna a sus archivos
CICLO = "2017-2018"
SUFIJO = "_J"

# Módulos requeridos (demografía, examen físico, laboratorio y cuestionario)
MODULOS = ["DEMO", "BMX", "BPX", "GHB", "GLU", "TRIGLY", "HDL", "DIQ"]

# URL base de descarga; el nombre de cada archivo es <MODULO><SUFIJO>.xpt
URL_BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles"

# Carpeta de informes asociada a cada actividad
CARPETA_ACTIVIDAD = {
    2: "02_clustering",
}


def ruta_figuras(actividad: int) -> Path:
    """Devuelve la carpeta de figuras de una actividad y la crea si no existe."""
    ruta = RUTA_INFORMES / CARPETA_ACTIVIDAD[actividad] / "figuras"
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta
