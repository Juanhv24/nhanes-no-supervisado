# Técnicas de aprendizaje no supervisado con NHANES

Proyecto del curso **Técnicas de Análisis No Supervisado** de la Especialización en Análisis
Estadístico para Ciencia de Datos (Universidad de La Salle). El repositorio reúne las actividades
del curso sobre una misma base de datos: la Encuesta Nacional de Examen de Salud y Nutrición
(NHANES) de Estados Unidos, ciclo 2017–2018.

| Actividad | Técnica | Notebook | Estado |
|---|---|---|---|
| 2 | Clustering con modelo de mezclas gaussianas (GMM) | `notebooks/02_clustering.ipynb` | Completa |
| 3 | Análisis de correspondencias simple y múltiple | `notebooks/03_correspondencias.ipynb` | Completa |
| 4 | Análisis factorial exploratorio | `notebooks/04_factorial.ipynb` | Completa |

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

## Actividad 3: perfiles sociodemográficos y estado glucémico

**Pregunta guía:** ¿qué perfiles sociodemográficos y de estilo de vida se asocian con el estado
glucémico de los adultos?

### Datos

A los módulos de la actividad 2 se suman tabaquismo, seguridad alimentaria y seguro médico. La
población son los adultos de 20 años o más, sin embarazo, con HbA1c disponible y datos completos
en las diez variables categóricas: **4.124 participantes**. El estado glucémico (normal,
prediabetes o diabetes) se define con los umbrales de HbA1c de la ADA.

### Metodología

1. Recodificación de las variables en categorías, agrupando las que tienen menos del 5 %.
2. Análisis de correspondencias simple entre el estado glucémico y el nivel educativo:
   chi-cuadrado, V de Cramér, residuos estandarizados, contribuciones y mapa perceptual.
3. Análisis de correspondencias múltiple con nueve variables activas (28 categorías) y el estado
   glucémico como variable suplementaria, con la corrección de Benzécri de la inercia.
4. Verificación con tablas cruzadas, chi-cuadrado y V de Cramér de cada variable activa.

### Resultados principales

- **ACS:** la diabetes disminuye del 20,2 % en quienes no terminaron el bachillerato al 11,8 % en
  quienes tienen formación universitaria, aunque la asociación es débil (V de Cramér = 0,068).
- **ACM:** las dos primeras dimensiones recogen el 88,7 % de la inercia corregida. La primera es
  un gradiente socioeconómico y la segunda un eje de edad y obesidad abdominal, sobre el cual se
  ordena el estado glucémico.
- Las asociaciones más intensas son con la edad (V = 0,289) y la obesidad abdominal (V = 0,227):
  la diabetes pasa del 2,5 % entre los 20 y 39 años al 24,7 % desde los 60 años. La pobreza y la
  seguridad alimentaria no muestran una asociación significativa.

**Limitaciones:** datos transversales, sin pesos muestrales, exclusión del 17 % de la población
(sobre todo por ingreso no reportado) y una sola medición de HbA1c.

## Actividad 4: dimensiones latentes del perfil cardiometabólico

**Pregunta guía:** ¿qué dimensiones latentes resumen el perfil cardiometabólico de los adultos?

### Datos

Se agregan cuatro módulos de laboratorio: insulina, colesterol total, perfil bioquímico (ALT, GGT
y ácido úrico) y proteína C reactiva de alta sensibilidad, además de la presión diastólica. La
población son los adultos de 20 años o más, sin embarazo, de la submuestra en ayunas con las
catorce mediciones completas: **2.043 participantes**.

### Metodología

1. Transformación logarítmica de las variables con asimetría mayor que 1.
2. Pertinencia: KMO, MSA por variable, prueba de Bartlett y determinante. Se retiran el colesterol
   total (MSA = 0,32) y el IMC (r = 0,91 con la cintura), y el análisis sigue con doce variables
   (KMO = 0,71).
3. Número de factores con el criterio de Kaiser, el análisis paralelo y el RMSR.
4. Extracción por ejes principales con las comunalidades acotadas en 1, para controlar un caso
   Heywood, y rotación promax.
5. Confiabilidad por factor con el alfa de Cronbach y validación externa de los puntajes
   factoriales con el diagnóstico de diabetes y el grupo de edad.

### Resultados principales

| Factor | Variables principales | Alfa de Cronbach |
|---|---|---|
| Adiposidad, resistencia a la insulina e inflamación | Cintura, insulina, PCR y HDL (negativo) | 0,72 |
| Glucémico | HbA1c y glucosa | 0,91 |
| Hemodinámico | Presión sistólica y diastólica | 0,61 |
| Hepático | ALT y GGT | 0,74 |

- Los cuatro factores explican el 52,6 % de la varianza común (RMSR = 0,042) y están
  correlacionados entre sí: el de adiposidad es el central (Φ = 0,53 con el hepático).
- Las personas con diagnóstico de diabetes puntúan más alto en los cuatro factores, sobre todo en
  el glucémico (d = 1,74) y en el de adiposidad (d = 0,85). Los factores hemodinámico y glucémico
  aumentan con la edad.

**Limitaciones:** el factor hemodinámico tiene solo dos variables y un caso Heywood, los datos son
transversales, no se emplean los pesos muestrales y cada marcador corresponde a una sola medición.

## Estructura del repositorio

```
nhanes-no-supervisado/
├── datos/
│   ├── crudos/           # archivos .xpt de NHANES (se descargan, no se versionan)
│   └── procesados/       # base depurada en parquet (no se versiona)
├── informes/
│   ├── 02_clustering/figuras/        # figuras generadas por cada notebook
│   ├── 03_correspondencias/figuras/
│   └── 04_factorial/figuras/
├── notebooks/
│   ├── 02_clustering.ipynb         # actividad 2: clustering con GMM
│   ├── 03_correspondencias.ipynb   # actividad 3: correspondencias simple y múltiple
│   └── 04_factorial.ipynb          # actividad 4: análisis factorial exploratorio
├── scripts/
│   └── descargar_datos.py
└── src/nhanes_no_supervisado/
    ├── config.py         # semilla, rutas y parámetros de NHANES
    ├── datos.py          # carga de módulos y unión por participante
    └── factorial.py      # KMO, Bartlett, ejes principales, rotaciones, análisis paralelo y alfa
```

## Reproducir el análisis

### En local (con [uv](https://docs.astral.sh/uv/))

```bash
git clone https://github.com/Juanhv24/nhanes-no-supervisado.git
cd nhanes-no-supervisado
uv sync
uv run python scripts/descargar_datos.py
```

Después se abre el notebook de la actividad (por ejemplo, `notebooks/02_clustering.ipynb`) con el kernel del entorno `.venv` del proyecto y se
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
