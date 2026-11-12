"""Carga de los módulos de NHANES y unión en una sola tabla por participante."""

import pandas as pd

from nhanes_no_supervisado.config import ARCHIVO_DEPURADO, RUTA_CRUDOS, SUFIJO

# Variables de interés por módulo: código original de NHANES -> nombre en el proyecto
VARIABLES = {
    "DEMO": {
        "RIDAGEYR": "edad",
        "RIAGENDR": "sexo",
        "RIDEXPRG": "embarazo",
        "DMDEDUC2": "educacion",
        "RIDRETH3": "raza_etnia",
        "INDFMPIR": "ingreso_pobreza",
    },
    "BMX": {"BMXWAIST": "cintura_cm", "BMXBMI": "imc"},
    "BPX": {
        "BPXSY1": "sistolica_1",
        "BPXSY2": "sistolica_2",
        "BPXSY3": "sistolica_3",
        "BPXSY4": "sistolica_4",
        "BPXDI1": "diastolica_1",
        "BPXDI2": "diastolica_2",
        "BPXDI3": "diastolica_3",
        "BPXDI4": "diastolica_4",
    },
    "GHB": {"LBXGH": "hba1c_pct"},
    # El peso de la submuestra en ayunas (WTSAF2YR) también aparece en INS y TRIGLY;
    # se toma solo de GLU para no duplicar la columna en la unión
    "GLU": {"LBXGLU": "glucosa_mgdl", "WTSAF2YR": "peso_ayuno"},
    "TRIGLY": {"LBXTR": "trigliceridos_mgdl"},
    "HDL": {"LBDHDD": "hdl_mgdl"},
    "DIQ": {"DIQ010": "diabetes_dx"},
    "SMQ": {"SMQ020": "fumo_100", "SMQ040": "fuma_actual"},
    "FSQ": {"FSDAD": "seguridad_alimentaria"},
    "HIQ": {"HIQ011": "seguro_medico"},
    "INS": {"LBXIN": "insulina_uuml"},
    "TCHOL": {"LBXTC": "colesterol_total_mgdl"},
    "BIOPRO": {
        "LBXSATSI": "alt_ul",
        "LBXSGTSI": "ggt_ul",
        "LBXSUA": "acido_urico_mgdl",
    },
    "HSCRP": {"LBXHSCRP": "pcr_mgl"},
}

# El formato XPT almacena los ceros como 5.4e-79, por ende todo valor menor a este umbral es cero
UMBRAL_CERO = 1e-70


def cargar_modulo(modulo: str) -> pd.DataFrame:
    """Lee un módulo XPT y devuelve SEQN junto con sus variables renombradas."""
    ruta = RUTA_CRUDOS / f"{modulo}{SUFIJO}.xpt"
    df = pd.read_sas(ruta, format="xport")

    columnas = VARIABLES[modulo]
    df = df[["SEQN", *columnas]].rename(columns=columnas)
    df["SEQN"] = df["SEQN"].astype("int64")

    numericas = df.columns.drop("SEQN")
    df[numericas] = df[numericas].mask(df[numericas].abs() < UMBRAL_CERO, 0.0)
    return df


def cargar_crudos() -> pd.DataFrame:
    """
    Une todos los módulos por SEQN, partiendo de la demografía.

    La unión es por la izquierda: se conservan todos los participantes y quedan
    como faltantes las mediciones que no se tomaron (por ejemplo, la glucosa en
    quienes no pertenecen a la submuestra en ayunas).
    """
    base = cargar_modulo("DEMO")
    for modulo in VARIABLES:
        if modulo == "DEMO":
            continue
        base = base.merge(cargar_modulo(modulo), on="SEQN", how="left", validate="one_to_one")

    # Presión sistólica y diastólica como promedio de las lecturas disponibles.
    # Una diastólica de 0 mmHg se registra cuando los ruidos se escuchan hasta el cero y no
    # corresponde a la presión real, por lo que se trata como faltante
    for presion in ["sistolica", "diastolica"]:
        lecturas = [f"{presion}_{i}" for i in range(1, 5)]
        if presion == "diastolica":
            base[lecturas] = base[lecturas].mask(base[lecturas] == 0)
        base[f"{presion}_mmhg"] = base[lecturas].mean(axis=1, skipna=True)
        base = base.drop(columns=lecturas)

    return base.set_index("SEQN")


def cargar_depurados() -> pd.DataFrame:
    """Lee la base depurada que guarda el notebook después de la limpieza."""
    return pd.read_parquet(ARCHIVO_DEPURADO)
