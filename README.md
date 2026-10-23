# Técnicas de aprendizaje no supervisado con NHANES

Proyecto del curso **Técnicas de Análisis No Supervisado** de la Especialización en Análisis
Estadístico para Ciencia de Datos (Universidad de La Salle). El repositorio reúne las actividades
del curso sobre una misma base de datos: la Encuesta Nacional de Examen de Salud y Nutrición
(NHANES) de Estados Unidos, ciclo 2017–2018.

| Actividad | Técnica | Notebook | Estado |
|---|---|---|---|
| 2 | Clustering con modelo de mezclas gaussianas (GMM) | `notebooks/nhanes.ipynb` | Completa |
| 3 | Análisis de correspondencias | — | Pendiente |
| 4 | Análisis factorial | — | Pendiente |

## Actividad 2: perfiles de riesgo cardiometabólico

**Pregunta guía:** ¿cómo podemos utilizar clustering para identificar perfiles de riesgo
cardiometabólico en adultos?

### Datos

Se unen ocho módulos del ciclo 2017–2018 por el identificador de participante (`SEQN`):
demografía, antropometría, presión arterial, HbA1c, glucosa en ayunas, triglicéridos, colesterol
HDL y diagnóstico de diabetes. La población de estudio son los adultos de 20 años o más, sin
embarazo, de la submuestra en ayunas con datos completos: **2.173 participantes**.

El modelo usa seis variables continuas, que corresponden a los componentes del síndrome
metabólico más la HbA1c. El diagnóstico de diabetes no entra al modelo: se reserva para la
validación externa.

### Metodología

1. Análisis exploratorio: faltantes por diseño de la encuesta, asimetría, atípicos y correlaciones
   de Spearman.
2. Preprocesamiento: transformación de Yeo-Johnson y estandarización.
3. Selección del modelo por BIC entre 1 y 8 grupos y cuatro estructuras de covarianza.
4. Ajuste final del GMM (K = 3, covarianza completa) con probabilidades de pertenencia.
5. Validación interna (silueta, Calinski-Harabasz, Davies-Bouldin), estabilidad entre 20
   reajustes y validación externa contra el diagnóstico de diabetes.
6. Perfilamiento clínico con los criterios del síndrome metabólico y los rangos glucémicos de la ADA.

### Resultados principales

| Grupo | Participantes | Rasgos principales |
|---|---|---|
| Perfil típico | 1.547 (71 %) | Valores cercanos a la normalidad; 62 % en rango de prediabetes |
| Alto riesgo | 552 (25 %) | HbA1c de 6,6 % y glucosa de 132 mg/dL (medianas); 64 % con síndrome metabólico |
| Grupo residual | 74 (3 %) | Componente inestable y heterogéneo; no se interpreta como perfil |

- Sin usar el diagnóstico, el grupo de alto riesgo concentra el **79 %** de los casos de diabetes
  autorreportada (V de Cramér = 0,407).
- El 36 % de los participantes tiene una probabilidad de pertenencia menor de 0,8: el riesgo
  cardiometabólico se comporta como un continuo, no como categorías separadas.

**Limitaciones:** no se emplean los pesos muestrales de NHANES, el diagnóstico es autorreportado y
el síndrome metabólico es una aproximación (sin presión diastólica ni tratamientos).

## Estructura del repositorio

```
nhanes-no-supervisado/
├── datos/
│   ├── crudos/           # archivos .xpt de NHANES (se descargan, no se versionan)
│   └── procesados/       # base depurada en parquet (no se versiona)
├── informes/
│   └── 02_clustering/
│       └── figuras/      # figuras generadas por el notebook
├── notebooks/
│   └── nhanes.ipynb      # análisis completo de la actividad 2
├── scripts/
│   └── descargar_datos.py
└── src/nhanes_no_supervisado/
    ├── config.py         # semilla, rutas y parámetros de NHANES
    └── datos.py          # carga de módulos y unión por participante
```

## Reproducir el análisis

### En local (con [uv](https://docs.astral.sh/uv/))

```bash
git clone https://github.com/Juanhv24/nhanes-no-supervisado.git
cd nhanes-no-supervisado
uv sync
uv run python scripts/descargar_datos.py
```

Después se abre `notebooks/nhanes.ipynb` con el kernel del entorno `.venv` del proyecto y se
ejecutan todas las celdas.

### En Google Colab

```python
!git clone https://github.com/Juanhv24/nhanes-no-supervisado.git
%cd nhanes-no-supervisado
!pip install -q -e .
!python scripts/descargar_datos.py
```

## Fuente de los datos

National Center for Health Statistics. (s.f.). *National Health and Nutrition Examination
Survey*. Centers for Disease Control and Prevention.
[Ciclo 2017–2018](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2017)

## Uso de inteligencia artificial

El análisis contó con el apoyo de Claude (Anthropic) como revisor del código y de los textos. El
alcance detallado está en la declaración de uso de IA de la entrega.
