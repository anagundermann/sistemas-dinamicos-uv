# Sistemas Dinámicos UV

Dashboard interactivo desarrollado en Python con Dash para explorar el comportamiento de sistemas dinámicos mediante simulaciones numéricas, visualizaciones y modificación de parámetros.

**Universidad de Valparaíso**  
**Asignatura:** IECD-421 — Visualización de Datos  
**Profesor:** Nicolás Rivera  
**Semestre:** Segundo semestre de 2026

## Integrantes

- Macarena Valdebenito
- Fabián Zanetta
- Ana Gundermann

## Objetivo

Facilitar la comprensión de distintos sistemas dinámicos mediante laboratorios interactivos que permiten modificar condiciones iniciales, observar trayectorias y analizar cómo evoluciona el comportamiento de cada modelo.

La aplicación tiene un propósito educativo y está dirigida a estudiantes y personas interesadas en las matemáticas aplicadas, las ecuaciones diferenciales y la simulación numérica.

## Laboratorios

### 1. Péndulo simple

Simulación de oscilaciones y amortiguamiento. Permite explorar trayectorias en el espacio de fases y observar la sensibilidad a las condiciones iniciales.

### 2. Péndulo doble

Simulación de un sistema dinámico no lineal que permite estudiar la sensibilidad a condiciones iniciales y el comportamiento caótico.

### 3. Depredador–Presa (Lotka–Volterra)

Modelo de interacción entre dos poblaciones. Permite modificar las tasas de crecimiento, depredación y mortalidad, observar la evolución temporal y analizar el plano de fases.

### 4. Modelo SIR

Simulación epidemiológica sobre una red simplificada de las 16 regiones de Chile. Permite explorar la propagación de una epidemia bajo distintos parámetros de transmisión, recuperación y conexión entre regiones.

## Tecnologías utilizadas

- Python y Dash para la estructura e interactividad de la aplicación.
- Plotly para los gráficos interactivos.
- NumPy y SciPy para el cálculo numérico.
- Pandas para el tratamiento de datos.
- NetworkX y Dash Cytoscape para representar redes y grafos.
- Dash Bootstrap Components para los elementos de interfaz.
- JavaScript para la simulación y animación de los péndulos.
- CSS y SVG para la presentación visual.
- R para la limpieza y preparación de los datos epidemiológicos.

## Instalación

Se recomienda utilizar Python 3.11.

Clonar el repositorio:

```bash
git clone https://github.com/anagundermann/sistemas-dinamicos-uv.git
cd sistemas-dinamicos-uv
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

Desde la carpeta principal del proyecto, ejecutar:

```bash
python app.py
```

Abrir en el navegador:

[http://127.0.0.1:8082/](http://127.0.0.1:8082/)

Para detener la aplicación, presionar `Ctrl + C` en la terminal.

## Métodos numéricos

Los modelos se resuelven mediante integración numérica de ecuaciones diferenciales ordinarias.

| Modelo | Método |
| --- | --- |
| Péndulo simple | Runge–Kutta clásico de orden 4 (RK4), paso fijo |
| Péndulo doble | Runge–Kutta clásico de orden 4 (RK4), paso fijo |
| Lotka–Volterra | RK45 adaptativo mediante `scipy.integrate.solve_ivp` |
| SIR | RK45 adaptativo mediante `scipy.integrate.solve_ivp` |

Los péndulos utilizan un motor de simulación implementado en JavaScript. Los modelos Lotka–Volterra y SIR realizan la integración numérica en Python.

## Datos y limitaciones

### Procedencia de los datos del laboratorio SIR

El conjunto de datos original corresponde a `Covid-19_std.csv`, del **Producto 1 del proyecto Datos-COVID19 del Ministerio de Ciencia, Tecnología, Conocimiento e Innovación de Chile (MinCiencia)**. La información procede de registros oficiales publicados por el Ministerio de Salud y fue organizada como datos abiertos para su análisis.

El archivo histórico utilizado abarca desde el **30 de marzo de 2020 hasta el 8 de enero de 2021**. Dado que el repositorio original de GitHub ya no está disponible en su antigua dirección, se incluye en las referencias una copia histórica preservada en Zenodo.

### Preparación de los datos

El procesamiento se realizó en **R**, mediante el script `analisis_datos/limpieza_covid.R`, para obtener el archivo `analisis_datos/covid_chile_regional_limpio.csv`, incluido en el proyecto.

El archivo procesado organiza la información por **16 regiones y 84 fechas**, con **1.344 registros** (una observación por región y fecha).

### Alcance de la simulación

- Los registros históricos representan **casos confirmados acumulados**; no equivalen directamente a personas infectadas activamente, que corresponden a la variable $I(t)$ del modelo SIR.
- Las poblaciones regionales se emplean para configurar la simulación, pero el modelo no está calibrado para reproducir exactamente la evolución histórica del COVID-19 en Chile.
- La red utilizada es una representación simplificada de conexiones entre regiones y no pretende describir con exactitud la movilidad real.
- Los modelos son herramientas educativas para estudiar fenómenos dinámicos y no deben interpretarse como predicciones epidemiológicas o ecológicas reales.

## Referencias

### Fundamentos matemáticos



### Documentación técnica

- Dash: [https://dash.plotly.com/](https://dash.plotly.com/)
- Dash Cytoscape: [https://dash.plotly.com/cytoscape](https://dash.plotly.com/cytoscape)
- SciPy, `solve_ivp`: [https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)
- NetworkX: [https://networkx.org/documentation/stable/](https://networkx.org/documentation/stable/)

### Datos y fuentes

#### Datos epidemiológicos de COVID-19

- **Ministerio de Ciencia, Tecnología, Conocimiento e Innovación de Chile.** *Base de Datos COVID-19*. [Sitio institucional de MinCiencia](https://www.minciencia.gob.cl/areas/minciencia-covid19/submesa-de-datos-covid19/).
- **MinCiencia.** *Datos-COVID19, Producto 1: `Covid-19_std.csv`*. Copia histórica del conjunto de datos, alojada por terceros en Zenodo: [https://doi.org/10.5281/zenodo.18773580](https://doi.org/10.5281/zenodo.18773580). Período de los registros: **30-03-2020 al 08-01-2021**.
- **Procesamiento para el proyecto:** limpieza y preparación de los datos mediante `analisis_datos/limpieza_covid.R`, con resultados almacenados en `analisis_datos/covid_chile_regional_limpio.csv`.

#### Datos geográficos para el grafo SIR

El archivo `capitales_regionales.csv` contiene las coordenadas geográficas aproximadas de las capitales de las **16 regiones de Chile**, utilizadas para representar espacialmente los nodos del grafo del modelo SIR.

El conjunto contiene 16 registros, uno por región, identificados mediante los mismos nombres utilizados en `covid_chile_regional_limpio.csv`. Sus columnas son `Region`, `Capital`, `Longitud` y `Latitud`. Las coordenadas están expresadas en grados decimales bajo el sistema de referencia **WGS84 (EPSG:4326)**.

**Fuentes y licencia:**

- **GeoNames.** Coordenadas geográficas de las capitales regionales, consultadas en noviembre de 2026: [Búsqueda avanzada de Chile](https://www.geonames.org/advanced-search.html?country=CL) y [registros adicionales, incluido Coyhaique](https://www.geonames.org/search.html?country=CL&startRow=100).
- **Licencia:** datos geográficos © GeoNames, distribuidos bajo **Creative Commons Attribution 4.0 (CC BY 4.0)**. Véanse los [términos y condiciones de GeoNames](https://www.geonames.org/export/). El archivo CSV corresponde a una selección de registros cuyas coordenadas fueron redondeadas a cinco decimales.
- **División administrativa:** la identificación de una capital por región se apoya en la [división administrativa de Chile de GeoNames](https://www.geonames.org/CL/administrative-division-chile.html), incluida la Región de Ñuble, cuya capital es Chillán.
- **Referencia cartográfica complementaria:** [IDE Chile – Capitales](https://geoportal.cl/index.php/geoportal/catalog/34996/Capitales). Esta capa cartográfica corresponde a 2013 y, por sí sola, no contempla las modificaciones administrativas posteriores.

## Uso de inteligencia artificial

Se utilizaron herramientas de inteligencia artificial para buscar ideas, comprender documentación, generar o corregir código y mejorar el diseño de la aplicación.

Los integrantes del equipo revisaron las decisiones principales del proyecto, el funcionamiento del código y los resultados obtenidos, con el propósito de verificar que la aplicación cumpla con los objetivos y funcionalidades descritos.
