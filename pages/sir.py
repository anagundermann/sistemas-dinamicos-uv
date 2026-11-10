from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import networkx as nx

from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# --------------------------------------------------
# 1. CARGA Y PROCESAMIENTO DE DATOS REALES DE CHILE
# --------------------------------------------------

REGIONES_ORDENADAS = [
    "Arica y Parinacota",
    "Tarapacá",
    "Antofagasta",
    "Atacama",
    "Coquimbo",
    "Valparaíso",
    "Metropolitana",
    "O’Higgins",
    "Maule",
    "Ñuble",
    "Biobío",
    "Araucanía",
    "Los Ríos",
    "Los Lagos",
    "Aysén",
    "Magallanes",
]

# Las coordenadas reales de las 16 capitales regionales se guardan en
# analisis_datos/capitales_regionales.csv (GeoNames, CC BY 4.0).
# No se mezclan con las posiciones del diagrama ni con los datos epidemiologicos.
RUTA_CAPITALES = (
    Path(__file__).resolve().parent.parent
    / "analisis_datos"
    / "capitales_regionales.csv"
)


def cargar_capitales_regionales():
    """Lee puntos WGS84 de capitales; verifica correspondencia con las regiones."""
    if not RUTA_CAPITALES.is_file():
        raise FileNotFoundError(
            f"Falta {RUTA_CAPITALES}. Copia capitales_regionales.csv "
            "dentro de analisis_datos/."
        )
    datos = pd.read_csv(RUTA_CAPITALES, encoding="utf-8-sig")
    obligatorias = {"Region", "Capital", "Longitud", "Latitud"}
    if not obligatorias.issubset(datos.columns):
        raise ValueError(f"El CSV de capitales necesita: {sorted(obligatorias)}")
    if datos["Region"].duplicated().any():
        raise ValueError("Hay regiones duplicadas en el CSV de capitales.")
    if set(datos["Region"]) != set(REGIONES_ORDENADAS):
        raise ValueError(
            "El CSV de capitales debe incluir las mismas 16 regiones del SIR."
        )
    if datos[list(obligatorias)].isna().any().any():
        raise ValueError("El CSV de capitales tiene datos faltantes.")
    datos = datos.set_index("Region").loc[REGIONES_ORDENADAS]
    if not datos["Longitud"].between(-77, -66).all():
        raise ValueError("Las longitudes de capitales parecen incorrectas.")
    if not datos["Latitud"].between(-56, -17).all():
        raise ValueError("Las latitudes de capitales parecen incorrectas.")
    return datos


CAPITALES = cargar_capitales_regionales()

# COORDS conserva la informacion geografica original: (longitud, latitud).
COORDS = {
    region: (
        float(CAPITALES.loc[region, "Longitud"]),
        float(CAPITALES.loc[region, "Latitud"]),
    )
    for region in REGIONES_ORDENADAS
}


# Ajustes EXCLUSIVAMENTE visuales: ninguna cifra modifica las capitales WGS84.
# Se conserva el orden norte-sur, pero se despejan vertices cercanos entre si.
DESPLAZAMIENTO_VERTICAL_GRAFO = {
    "Arica y Parinacota": 1.5,
    "Tarapacá": -2.0,
    "Antofagasta": 1.0,
    "Atacama": -2.0,
    "Coquimbo": 2.5,
    "Valparaíso": -1.5,
    "Metropolitana": 3.0,
    "O’Higgins": -2.0,
    "Maule": 1.0,
    "Ñuble": -1.5,
    "Biobío": -0.5,
    "Araucanía": 1.0,
    "Los Ríos": -1.0,
    "Los Lagos": 1.5,
    "Aysén": -0.5,
    "Magallanes": 0.0,
}


def construir_posiciones_esquematicas():
    """Posiciones norte-sur con separación visual, no mapa a escala.

    Las coordenadas originales COORDS permanecen intactas. El eje horizontal
    combina latitud y orden; el eje vertical muestra la diferencia este-oeste
    atenuada más un desplazamiento suave para despejar el centro del grafo.
    """
    latitudes_sur = [-COORDS[region][1] for region in REGIONES_ORDENADAS]
    extremo_norte, extremo_sur = min(latitudes_sur), max(latitudes_sur)
    posiciones = {}
    total = len(REGIONES_ORDENADAS)
    for indice, region in enumerate(REGIONES_ORDENADAS):
        longitud, latitud = COORDS[region]
        avance_geografico = (-latitud - extremo_norte) / (extremo_sur - extremo_norte)
        avance_ordenado = indice / (total - 1)
        x = 8.0 + 84.0 * (0.25 * avance_geografico + 0.75 * avance_ordenado)
        y = (longitud + 71.6) * 7.0 + DESPLAZAMIENTO_VERTICAL_GRAFO[region]
        posiciones[region] = (x, y)
    return posiciones


POSICIONES_GRAFO = construir_posiciones_esquematicas()

# Desplazamiento en pixeles de las etiquetas respecto de los vertices.
# ax: derecha (+) / izquierda (-); ay: abajo (+) / arriba (-).
# Las lineas guia evitan confundir a que nodo corresponde cada etiqueta.
ETIQUETAS_GRAFO = {
    "Arica y Parinacota": (0, -30),
    "Tarapacá": (0, 31),
    "Antofagasta": (0, -30),
    "Atacama": (0, 30),
    "Coquimbo": (-9, -34),
    "Valparaíso": (-16, 33),
    "Metropolitana": (16, -36),
    "O’Higgins": (30, 33),
    "Maule": (-14, -32),
    "Ñuble": (8, 34),
    "Biobío": (-30, 32),
    "Araucanía": (14, -34),
    "Los Ríos": (-24, 32),
    "Los Lagos": (22, 34),
    "Aysén": (0, -30),
    "Magallanes": (0, -30),
}


def cargar_poblaciones_chile():
    """Obtiene poblaciones regionales del CSV preparado en R.

    Los casos acumulados del archivo son observaciones historicas y no
    equivalen a los infectados activos I(t) del modelo SIR. Por eso no
    participan en la simulacion ni se dibujan sobre sus curvas.
    """
    ruta_csv = (
        Path(__file__).resolve().parent.parent
        / "analisis_datos"
        / "covid_chile_regional_limpio.csv"
    )
    if not ruta_csv.is_file():
        raise FileNotFoundError(
            "No se encontro el CSV regional limpio: "
            f"{ruta_csv}. Ejecuta la limpieza en R antes de abrir SIR."
        )

    datos = pd.read_csv(
        ruta_csv,
        encoding="utf-8-sig",
        usecols=["Region", "Poblacion"],
    )
    if datos[["Region", "Poblacion"]].isna().any().any():
        raise ValueError("Hay regiones o poblaciones faltantes en el CSV.")
    if set(datos["Region"]) != set(REGIONES_ORDENADAS):
        raise ValueError("El CSV debe contener exactamente las 16 regiones de Chile.")
    if (datos.groupby("Region")["Poblacion"].nunique() != 1).any():
        raise ValueError("Una region tiene distintas poblaciones segun la fecha.")
    if (datos["Poblacion"] <= 0).any():
        raise ValueError("Las poblaciones regionales deben ser positivas.")

    poblaciones = datos.groupby("Region")["Poblacion"].first()
    return {region: float(poblaciones[region]) for region in REGIONES_ORDENADAS}


POBLACIONES = cargar_poblaciones_chile()
N_VEC = np.array([POBLACIONES[r] for r in REGIONES_ORDENADAS], dtype=float)


def construir_grafo_chile():
    G = nx.Graph()
    for r in REGIONES_ORDENADAS:
        G.add_node(r, pos=COORDS[r])

    for i in range(len(REGIONES_ORDENADAS) - 1):
        G.add_edge(REGIONES_ORDENADAS[i], REGIONES_ORDENADAS[i + 1], weight=1.0)

    hubs = [
        "Antofagasta",
        "Coquimbo",
        "Valparaíso",
        "Biobío",
        "Araucanía",
        "Los Lagos",
        "Magallanes",
    ]
    for h in hubs:
        if not G.has_edge("Metropolitana", h):
            G.add_edge("Metropolitana", h, weight=0.6)

    return G


GRAFO_CHILE = construir_grafo_chile()
MATRIZ_ADYACENCIA = nx.to_numpy_array(GRAFO_CHILE, nodelist=REGIONES_ORDENADAS)


def sir_network_ode(t, y, num_nodes, beta, gamma, alpha, adj, N_vec):
    S = y[:num_nodes]
    I = y[num_nodes : 2 * num_nodes]
    R = y[2 * num_nodes :]

    I_over_N = I / N_vec

    dSdt = np.zeros(num_nodes)
    dIdt = np.zeros(num_nodes)
    dRdt = np.zeros(num_nodes)

    for i in range(num_nodes):
        local_inf = beta * S[i] * I_over_N[i]
        net_inf = alpha * S[i] * np.dot(adj[i, :], I_over_N)
        total_inf = local_inf + net_inf

        dSdt[i] = -total_inf
        dIdt[i] = total_inf - gamma * I[i]
        dRdt[i] = gamma * I[i]

    return np.concatenate([dSdt, dIdt, dRdt])


def simular_sir_grafo(beta, gamma, alpha, region_semilla, dias=180):
    num_nodes = len(REGIONES_ORDENADAS)
    idx_semilla = (
        REGIONES_ORDENADAS.index(region_semilla)
        if region_semilla in REGIONES_ORDENADAS
        else 6
    )

    I0 = np.zeros(num_nodes)
    I0[idx_semilla] = 1000.0
    S0 = N_VEC - I0
    R0 = np.zeros(num_nodes)

    y0 = np.concatenate([S0, I0, R0])
    t_span = (0, dias)
    t_eval = np.linspace(0, dias, dias + 1)

    sol = solve_ivp(
        sir_network_ode,
        t_span,
        y0,
        args=(num_nodes, beta, gamma, alpha, MATRIZ_ADYACENCIA, N_VEC),
        t_eval=t_eval,
        method="RK45",
    )

    return (
        sol.t,
        sol.y[:num_nodes, :],
        sol.y[num_nodes : 2 * num_nodes, :],
        sol.y[2 * num_nodes :, :],
    )


# --------------------------------------------------
# 2. MODALES INFORMATIVOS
# --------------------------------------------------
# Los tres modales se definen aqui; no se requiere modal_supuestos_sir.py.


def _sir_caja_modal(titulo, contenido):
    return html.Div(
        className="sir-modal-caja",
        children=[
            html.H6(titulo, className="sir-modal-caja-titulo"),
            html.P(contenido, className="sir-modal-parrafo"),
        ],
    )


def _sir_modal_base(
    identificador, titulo, contenido, boton_id, rosado=False, size="lg"
):
    return dbc.Modal(
        id=identificador,
        is_open=False,
        centered=True,
        scrollable=True,
        size=size,
        className="sir-modal sir-modal-rosa" if rosado else "sir-modal",
        children=[
            dbc.ModalHeader(dbc.ModalTitle(titulo), close_button=False),
            dbc.ModalBody(contenido),
            dbc.ModalFooter(
                dbc.Button(
                    "Cerrar",
                    id=boton_id,
                    n_clicks=0,
                    className="sir-modal-cerrar",
                )
            ),
        ],
    )


def crear_modal_definicion_sir():
    return _sir_modal_base(
        "modal-sir",
        "Definición: modelo SIR en redes complejas",
        [
            _sir_caja_modal(
                "Enfoque compartimental",
                "El modelo SIR divide la población en tres estados: Susceptibles (S), "
                "Infectados (I) y Recuperados (R). Cada región tiene su propia "
                "población, y los flujos entre estados dependen de los parámetros "
                "de transmisión y recuperación.",
            ),
            _sir_caja_modal(
                "Red de conectividad regional",
                "La simulación conecta las 16 regiones de Chile mediante un grafo "
                "ilustrativo. Las aristas representan canales de transmisión "
                "interregional asociados a un modelo de movilidad simplificado.",
            ),
        ],
        "btn-cerrar-modal-sir",
    )


def crear_modal_matematico_sir():
    """Modal compacto: ecuaciones en dos filas y definiciones en tres columnas."""
    formulas = [
        (
            "Susceptibles",
            r"$$\frac{dS_i}{dt}=-\beta\frac{S_iI_i}{N_i}-\alpha S_i\sum_j A_{ij}\frac{I_j}{N_j}$$",
        ),
        (
            "Infectados",
            r"$$\frac{dI_i}{dt}=\beta\frac{S_iI_i}{N_i}+\alpha S_i\sum_j A_{ij}\frac{I_j}{N_j}-\gamma I_i$$",
        ),
        ("Recuperados", r"$$\frac{dR_i}{dt}=\gamma I_i$$"),
    ]
    return _sir_modal_base(
        "modal-mat",
        "Modelo matemático · COVID-19 en redes",
        [
            html.P(
                "Modelo SIR regional acoplado por una matriz de adyacencia. "
                "Los parámetros β, γ y α regulan, respectivamente, la infección "
                "local, la recuperación y la transmisión entre regiones.",
                className="sir-modal-parrafo",
            ),
            # Fila 1: Susceptibles e Infectados, mitad y mitad.
            # Fila 2: Recuperados (1/3) y Condiciones iniciales (2/3).
            html.Div(
                className="sir-matematico-ecuaciones",
                children=[
                    *[
                        html.Div(
                            className=(
                                "sir-modal-formula sir-matematico-principal"
                                if indice < 2
                                else "sir-modal-formula sir-matematico-recuperados"
                            ),
                            children=[
                                html.Strong(nombre),
                                dcc.Markdown(expresion, mathjax=True),
                            ],
                        )
                        for indice, (nombre, expresion) in enumerate(formulas)
                    ],
                    html.Div(
                        className="sir-modal-caja sir-matematico-iniciales",
                        children=[
                            html.H6(
                                "Condiciones iniciales",
                                className="sir-modal-caja-titulo",
                            ),
                            dcc.Markdown(
                                r"$$I_i(0)=1000\text{ (región semilla)},"
                                r"\qquad S_i(0)=N_i-I_i(0),\quad R_i(0)=0$$",
                                mathjax=True,
                            ),
                            html.P(
                                "En las demás regiones Iᵢ(0)=0. Las poblaciones se conectan "
                                "mediante la matriz de adyacencia del grafo. Integración "
                                "numérica RK45 durante 180 días.",
                                className="sir-modal-parrafo",
                            ),
                        ],
                    ),
                ],
            ),
            # Tres columnas por dos filas; todas las tarjetas tienen separación.
            html.Div(
                className="sir-modal-cuadricula sir-matematico-definiciones",
                children=[
                    _sir_caja_modal(
                        "Estados por región",
                        "Sᵢ(t), Iᵢ(t), Rᵢ(t): susceptibles, infectados y recuperados en la región i.",
                    ),
                    _sir_caja_modal(
                        "Población regional",
                        "Nᵢ: población total de la región, constante durante la simulación.",
                    ),
                    _sir_caja_modal(
                        "β · Infección local",
                        "Tasa de transmisión dentro de una misma región.",
                    ),
                    _sir_caja_modal(
                        "γ · Recuperación",
                        "Inverso del período infeccioso en el modelo.",
                    ),
                    _sir_caja_modal(
                        "α · Movilidad en red",
                        "Coeficiente de transmisión entre regiones conectadas.",
                    ),
                    _sir_caja_modal(
                        "Significado de la red",
                        "Aᵢⱼ representa la conectividad entre las regiones i y j. "
                        "El término α·Sᵢ·Σⱼ(Aᵢⱼ·Iⱼ/Nⱼ) incorpora la transmisión "
                        "proveniente de las regiones conectadas.",
                    ),
                ],
            ),
        ],
        "btn-cerrar-modal-mat",
        size="xl",
    )


def crear_modal_supuestos_sir():
    return _sir_modal_base(
        "modal-supuestos-sir",
        "Supuestos del modelo y fuentes de datos",
        [
            html.P(
                "Laboratorio educativo de propagación epidémica en las 16 "
                "regiones de Chile.",
                className="sir-modal-parrafo",
            ),
            html.Div(
                className="sir-modal-cuadricula",
                children=[
                    _sir_caja_modal(
                        "Población y constantes",
                        "En cada región, Sᵢ + Iᵢ + Rᵢ = Nᵢ. Las tasas β, γ y α "
                        "son constantes durante los 180 días simulados (RK45).",
                    ),
                    _sir_caja_modal(
                        "Red de contactos",
                        "La epidemia comienza con 1.000 infectados en la región "
                        "semilla. La conectividad regional es una representación "
                        "ilustrativa, no una medición real de contactos.",
                    ),
                    _sir_caja_modal(
                        "Datos de referencia",
                        "Las poblaciones regionales provienen del CSV preparado "
                        "en R a partir de MINCiencia. Los casos acumulados "
                        "históricos no son los infectados activos I(t) del modelo.",
                    ),
                    _sir_caja_modal(
                        "Alcance educativo",
                        "No se modelan reinfecciones, cambios demográficos ni "
                        "cuarentenas dinámicas. Los resultados son escenarios "
                        "matemáticos, no predicciones sanitarias.",
                    ),
                ],
            ),
        ],
        "btn-cerrar-modal-supuestos-sir",
        rosado=True,
        size="xl",
    )


# --------------------------------------------------
# 3. ELEMENTOS REUTILIZABLES DE LA INTERFAZ
# --------------------------------------------------


def _sir_indicador(titulo, valor_id, pie_id=None, pie=None, extra_clase=""):
    pie_elemento = (
        html.Span(id=pie_id, children=pie or "") if pie_id else html.Span(pie or "")
    )
    return html.Div(
        className=f"sir-indicador {extra_clase}".strip(),
        children=[
            html.Div(titulo, className="sir-indicador-etiqueta"),
            html.Strong(id=valor_id, children="--", className="sir-indicador-valor"),
            html.Div(pie_elemento, className="sir-indicador-pie"),
        ],
    )


def _sir_control_slider(
    titulo, identificador, minimo, maximo, paso, valor, marcas, id_valor
):
    return html.Div(
        className="sir-control-grupo",
        children=[
            html.Div(
                className="sir-control-linea",
                children=[
                    html.Label(titulo, htmlFor=identificador),
                    dcc.Input(
                        id=id_valor,
                        type="number",
                        min=minimo,
                        max=maximo,
                        step=paso,
                        value=valor,
                        debounce=True,
                        className="sir-control-valor",
                        style={"width": "62px", "height": "30px"},
                    ),
                ],
            ),
            dcc.Slider(
                id=identificador,
                min=minimo,
                max=maximo,
                step=paso,
                value=valor,
                marks=marcas,
                allow_direct_input=False,  # Dash 4 agrega un campo numerico automatico.
            ),
        ],
    )


def _sir_grafico(identificador):
    return dcc.Graph(
        id=identificador,
        className="sir-grafico",
        style={"height": "100%", "width": "100%"},
        responsive=True,
        config={"displayModeBar": False, "responsive": True},
    )


def crear_pagina():
    """Opcion 2: portada, indicadores, controles laterales y grafico con pestanas.

    Todo el layout usa clases sir-; los colores se editan en assets/zz-sir.css.
    """
    return html.Div(
        className="sir-pagina",
        children=[
            # Cabecera propia del laboratorio + indicadores del escenario.
            html.Div(
                className="sir-resumen-superior",
                children=[
                    html.Section(
                        className="sir-hero",
                        children=[
                            html.Div(
                                className="sir-hero-texto",
                                children=[
                                    html.Div("MODELO SIR", className="sir-hero-rotulo"),
                                    html.H2("Propagación epidémica en Chile"),
                                    html.P(
                                        "Explora cómo evolucionan las poblaciones "
                                        "susceptibles, infectadas y recuperadas "
                                        "en una red de 16 regiones."
                                    ),
                                ],
                            ),
                            html.Div("S · I · R", className="sir-hero-marca"),
                        ],
                    ),
                    html.Div(
                        className="sir-indicadores",
                        children=[
                            _sir_indicador(
                                "β/γ · Referencia local",
                                "sir-kpi-r0",
                                "sir-kpi-r0-desc",
                                extra_clase="sir-indicador-r0",
                            ),
                            _sir_indicador(
                                "Pico máximo · Iₘₐₓ",
                                "sir-kpi-imax",
                                "sir-kpi-tmax",
                                extra_clase="sir-indicador-pico",
                            ),
                            _sir_indicador(
                                "Umbral teórico sin red",
                                "sir-kpi-rebaño",
                                pie="Referencia SIR homogéneo",
                                extra_clase="sir-indicador-umbral",
                            ),
                        ],
                    ),
                ],
            ),
            # Barra informativa y acceso a modales.
            html.Div(
                className="sir-barra-info",
                children=[
                    html.Div(
                        className="sir-barra-titulo",
                        children=[
                            html.Strong("Laboratorio COVID-19 en Redes de Chile"),
                            html.Span("Modelo epidemiológico de transmisión regional"),
                        ],
                    ),
                    html.Div(
                        className="sir-barra-acciones",
                        children=[
                            html.Button(
                                "¿Qué es el Modelo SIR?",
                                id="btn-abrir-modal-sir",
                                n_clicks=0,
                                className="sir-boton sir-boton-violeta",
                            ),
                            html.Button(
                                "Modelo matemático",
                                id="btn-abrir-modal-mat",
                                n_clicks=0,
                                className="sir-boton sir-boton-violeta",
                            ),
                            html.Button(
                                "Supuestos y datos",
                                id="btn-abrir-modal-supuestos-sir",
                                n_clicks=0,
                                className="sir-boton sir-boton-rosa",
                            ),
                        ],
                    ),
                ],
            ),
            # Los modales pueden montarse aqui y funcionan independientemente del layout.
            crear_modal_definicion_sir(),
            crear_modal_matematico_sir(),
            crear_modal_supuestos_sir(),
            # Dos columnas: controles siempre visibles / un grafico grande por vez.
            html.Div(
                className="sir-zona-trabajo",
                children=[
                    html.Section(
                        className="sir-panel sir-panel-controles",
                        children=[
                            html.H3(
                                "Parámetros del modelo", className="sir-panel-titulo"
                            ),
                            html.Div(
                                className="sir-controles-epidemicos",
                                children=[
                                    _sir_control_slider(
                                        "β · Tasa de infección",
                                        "sir-slider-beta",
                                        0.05,
                                        0.80,
                                        0.01,
                                        0.30,
                                        {0.05: "0.05", 0.4: "0.40", 0.8: "0.80"},
                                        "sir-valor-beta",
                                    ),
                                    _sir_control_slider(
                                        "γ · Recuperación",
                                        "sir-slider-gamma",
                                        0.02,
                                        0.40,
                                        0.01,
                                        0.10,
                                        {0.02: "0.02", 0.2: "0.20", 0.4: "0.40"},
                                        "sir-valor-gamma",
                                    ),
                                    _sir_control_slider(
                                        "α · Transmisión entre regiones",
                                        "sir-slider-alpha",
                                        0.0,
                                        0.15,
                                        0.005,
                                        0.03,
                                        {0.0: "Aislado", 0.075: "Medio", 0.15: "Alto"},
                                        "sir-valor-alpha",
                                    ),
                                ],
                            ),
                            html.H4(
                                "Configuración de la simulación",
                                className="sir-panel-subtitulo",
                            ),
                            html.Div(
                                className="sir-control-grupo sir-control-select",
                                children=[
                                    html.Label(
                                        "Región semilla (I₀)",
                                        htmlFor="sir-drop-semilla",
                                    ),
                                    dcc.Dropdown(
                                        id="sir-drop-semilla",
                                        options=[
                                            {"label": r, "value": r}
                                            for r in REGIONES_ORDENADAS
                                        ],
                                        value="Metropolitana",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="sir-control-grupo sir-control-select",
                                children=[
                                    html.Label(
                                        "Región de análisis", htmlFor="sir-drop-region"
                                    ),
                                    dcc.Dropdown(
                                        id="sir-drop-region",
                                        options=[
                                            {"label": "Nacional", "value": "Nacional"}
                                        ]
                                        + [
                                            {"label": r, "value": r}
                                            for r in REGIONES_ORDENADAS
                                        ],
                                        value="Nacional",
                                        clearable=False,
                                    ),
                                ],
                            ),
                            _sir_control_slider(
                                "Día a inspeccionar",
                                "sir-slider-dia-grafo",
                                0,
                                180,
                                1,
                                45,
                                {0: "Día 0", 90: "90", 180: "180"},
                                "sir-valor-dia",
                            ),
                            html.Div(
                                className="sir-nota-modelo",
                                children=[
                                    html.Strong("Modelo educativo · RK45"),
                                    html.Span(
                                        "180 días · Red ilustrativa de 16 regiones"
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Section(
                        className="sir-panel sir-panel-visualizacion",
                        children=[
                            html.Div(
                                className="sir-tabs-contenedor",
                                children=[
                                    dcc.Tabs(
                                        id="sir-tabs-graficos",
                                        value="tab-curvas",
                                        className="sir-tabs",
                                        mobile_breakpoint=0,
                                        style={
                                            "display": "flex",
                                            "flexDirection": "row",
                                            "flexWrap": "nowrap",
                                            "width": "100%",
                                        },
                                        children=[
                                            dcc.Tab(
                                                label="Curvas temporales S–I–R",
                                                value="tab-curvas",
                                                className="sir-tab",
                                                selected_className="sir-tab--seleccionada",
                                                style={"flex": "1 1 0", "minWidth": 0},
                                                selected_style={
                                                    "flex": "1 1 0",
                                                    "minWidth": 0,
                                                },
                                            ),
                                            dcc.Tab(
                                                label="Grafo espacial de Chile",
                                                value="tab-grafo",
                                                className="sir-tab",
                                                selected_className="sir-tab--seleccionada",
                                                style={"flex": "1 1 0", "minWidth": 0},
                                                selected_style={
                                                    "flex": "1 1 0",
                                                    "minWidth": 0,
                                                },
                                            ),
                                            dcc.Tab(
                                                label="Matriz espacio-temporal",
                                                value="tab-heatmap",
                                                className="sir-tab",
                                                selected_className="sir-tab--seleccionada",
                                                style={"flex": "1 1 0", "minWidth": 0},
                                                selected_style={
                                                    "flex": "1 1 0",
                                                    "minWidth": 0,
                                                },
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        _sir_grafico("sir-grafico-principal"),
                                        className="sir-vista-grafico",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="sir-resultados",
                                children=[
                                    html.Div(
                                        className="sir-resultados-valores",
                                        children=[
                                            html.Div(
                                                className="sir-resultados-encabezado",
                                                children=[
                                                    html.Strong("Estado del sistema"),
                                                    html.Span(
                                                        id="sir-dia-resultado",
                                                        children="Día 45",
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="sir-resultados-filas",
                                                children=[
                                                    html.Div(
                                                        [
                                                            html.Span("S"),
                                                            html.Strong(
                                                                id="sir-resultado-s"
                                                            ),
                                                        ],
                                                        className="sir-valor-s",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Span("I"),
                                                            html.Strong(
                                                                id="sir-resultado-i"
                                                            ),
                                                        ],
                                                        className="sir-valor-i",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Span("R"),
                                                            html.Strong(
                                                                id="sir-resultado-r"
                                                            ),
                                                        ],
                                                        className="sir-valor-r",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="sir-resultados-interpretacion",
                                        children=[
                                            html.Strong("Lectura del escenario"),
                                            html.P(
                                                id="sir-interpretacion",
                                                children="Elige parámetros y observa el resultado de la simulación.",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


# --------------------------------------------------
# 4. CALLBACKS
# --------------------------------------------------


def registrar_callbacks(app):
    """Registra modales y simulacion sin cambiar las ecuaciones originales."""

    def registrar_modal(id_modal, id_abrir, id_cerrar):
        @app.callback(
            Output(id_modal, "is_open"),
            Input(id_abrir, "n_clicks"),
            Input(id_cerrar, "n_clicks"),
            State(id_modal, "is_open"),
            prevent_initial_call=True,
        )
        def alternar_modal(n_abrir, n_cerrar, abierto):
            if ctx.triggered_id == id_abrir:
                return True
            if ctx.triggered_id == id_cerrar:
                return False
            return abierto

    registrar_modal("modal-sir", "btn-abrir-modal-sir", "btn-cerrar-modal-sir")
    registrar_modal("modal-mat", "btn-abrir-modal-mat", "btn-cerrar-modal-mat")
    registrar_modal(
        "modal-supuestos-sir",
        "btn-abrir-modal-supuestos-sir",
        "btn-cerrar-modal-supuestos-sir",
    )

    # Un solo callback circular por parametro evita cadenas entre callbacks.
    # En Dash >= 4 se usa la casilla morada personalizada, no la automatica.
    def vincular_numero_y_slider(id_slider, id_numero, minimo, maximo, paso):
        @app.callback(
            Output(id_slider, "value"),
            Output(id_numero, "value"),
            Input(id_slider, "value"),
            Input(id_numero, "value"),
            prevent_initial_call=True,
        )
        def sincronizar_valores(valor_slider, valor_numero):
            if ctx.triggered_id == id_numero:
                if valor_numero is None:
                    return valor_slider, valor_slider
                nuevo = min(max(float(valor_numero), minimo), maximo)
                nuevo = minimo + round((nuevo - minimo) / paso) * paso
                nuevo = round(min(max(nuevo, minimo), maximo), 6)
                if paso == 1:
                    nuevo = int(nuevo)
                return nuevo, nuevo
            return valor_slider, valor_slider

    vincular_numero_y_slider("sir-slider-beta", "sir-valor-beta", 0.05, 0.80, 0.01)
    vincular_numero_y_slider("sir-slider-gamma", "sir-valor-gamma", 0.02, 0.40, 0.01)
    vincular_numero_y_slider("sir-slider-alpha", "sir-valor-alpha", 0.0, 0.15, 0.005)
    vincular_numero_y_slider("sir-slider-dia-grafo", "sir-valor-dia", 0, 180, 1)

    @app.callback(
        Output("sir-kpi-r0", "children"),
        Output("sir-kpi-r0-desc", "children"),
        Output("sir-kpi-imax", "children"),
        Output("sir-kpi-tmax", "children"),
        Output("sir-kpi-rebaño", "children"),
        Output("sir-grafico-principal", "figure"),
        Output("sir-resultado-s", "children"),
        Output("sir-resultado-i", "children"),
        Output("sir-resultado-r", "children"),
        Output("sir-dia-resultado", "children"),
        Output("sir-interpretacion", "children"),
        Input("sir-slider-beta", "value"),
        Input("sir-slider-gamma", "value"),
        Input("sir-slider-alpha", "value"),
        Input("sir-drop-semilla", "value"),
        Input("sir-drop-region", "value"),
        Input("sir-slider-dia-grafo", "value"),
        Input("sir-tabs-graficos", "value"),
    )
    def actualizar_laboratorio_sir(
        beta, gamma, alpha, semilla, region_sel, dia_grafo, pestana
    ):
        dias = 180
        t, S_mat, I_mat, R_mat = simular_sir_grafo(
            beta, gamma, alpha, semilla, dias=dias
        )

        r0 = beta / gamma
        str_r0 = f"{r0:.2f}"
        desc_r0 = "No incluye transmisión en red"
        S_nac = np.sum(S_mat, axis=0)
        I_nac = np.sum(I_mat, axis=0)
        R_nac = np.sum(R_mat, axis=0)
        N_total = np.sum(N_VEC)

        idx_pico = np.argmax(I_nac)
        i_max_val = I_nac[idx_pico] / N_total * 100.0
        t_max_val = t[idx_pico]
        str_rebano = f"{(1.0 - 1.0 / r0) * 100.0:.1f}%" if r0 > 1.0 else "N/A"
        str_imax = f"{i_max_val:.2f}%"
        str_tmax = f"Día {int(t_max_val)}"

        dia_idx = min(max(int(45 if dia_grafo is None else dia_grafo), 0), dias)
        I_dia = I_mat[:, dia_idx]
        prevalencia_dia = I_dia / N_VEC * 100.0

        # Grafo regional: mismos nodos, aristas y prevalencias que en Maca.
        # POSICIONES_GRAFO es SOLO para visualizar; COORDS sigue siendo WGS84.
        # Las conexiones conservan su naturaleza ilustrativa.
        edge_x, edge_y = [], []
        for origen, destino in GRAFO_CHILE.edges():
            x0, y0 = POSICIONES_GRAFO[origen]
            x1, y1 = POSICIONES_GRAFO[destino]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        trace_edges = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=1.4, color="#CAD2E6"),
            hoverinfo="none",
            showlegend=False,
        )
        node_hover = [
            (
                f"<b>{r}</b> · {CAPITALES.loc[r, 'Capital']}"
                f"<br>Lat.: {COORDS[r][1]:.2f}° · Lon.: {COORDS[r][0]:.2f}°"
                f"<br>Infectados simulados: {int(I_dia[i]):,}"
                f"<br>Prevalencia simulada: {prevalencia_dia[i]:.2f}%"
            )
            for i, r in enumerate(REGIONES_ORDENADAS)
        ]
        etiquetas = [
            "Arica",
            "Tarapacá",
            "Antofagasta",
            "Atacama",
            "Coquimbo",
            "Valparaíso",
            "Metropolitana",
            "O’Higgins",
            "Maule",
            "Ñuble",
            "Biobío",
            "Araucanía",
            "Los Ríos",
            "Los Lagos",
            "Aysén",
            "Magallanes",
        ]
        poblacion_maxima = max(POBLACIONES.values())
        tamanos_vertices = [
            9.0 + 13.0 * np.sqrt(POBLACIONES[region] / poblacion_maxima)
            for region in REGIONES_ORDENADAS
        ]
        trace_nodes = go.Scatter(
            x=[POSICIONES_GRAFO[r][0] for r in REGIONES_ORDENADAS],
            y=[POSICIONES_GRAFO[r][1] for r in REGIONES_ORDENADAS],
            mode="markers",
            hovertext=node_hover,
            hoverinfo="text",
            showlegend=False,
            marker=dict(
                showscale=True,
                colorscale="Purples",
                color=prevalencia_dia,
                size=tamanos_vertices,
                colorbar=dict(
                    thickness=12,
                    len=0.72,
                    y=0.47,
                    yanchor="middle",
                    title=dict(text="% Inf.", font=dict(size=10)),
                ),
                line=dict(width=1, color="#FFFFFF"),
            ),
        )
        # Etiquetas independientes de los marcadores: conectadas con lineas
        # discretas y desplazables desde ETIQUETAS_GRAFO si Maca lo desea.
        etiquetas_anotaciones = [
            dict(
                x=POSICIONES_GRAFO[region][0],
                y=POSICIONES_GRAFO[region][1],
                xref="x",
                yref="y",
                text=etiqueta,
                ax=ETIQUETAS_GRAFO[region][0],
                ay=ETIQUETAS_GRAFO[region][1],
                showarrow=True,
                arrowhead=0,
                arrowwidth=0.8,
                arrowsize=1,
                arrowcolor="rgba(97, 90, 140, 0.42)",
                font=dict(size=11, color="#334155"),
                bgcolor="rgba(255, 255, 255, 0.9)",
                borderpad=1,
            )
            for region, etiqueta in zip(REGIONES_ORDENADAS, etiquetas)
        ]
        fig_grafo = go.Figure(data=[trace_edges, trace_nodes])
        fig_grafo.update_layout(
            title=dict(
                text=(
                    f"Red regional de Chile — Día {dia_idx}"
                    "<br><sup>Capitales: GeoNames (CC BY 4.0) · "
                    "esquema norte-sur, no a escala · conexiones ilustrativas</sup>"
                ),
                font=dict(size=15, color="#24204A"),
                x=0.02,
                xanchor="left",
            ),
            margin=dict(l=38, r=74, t=78, b=34),
            xaxis=dict(
                range=[0, 100],
                domain=[0.03, 0.97],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                fixedrange=True,
            ),
            yaxis=dict(
                range=[-21, 20],
                domain=[0.09, 0.90],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                fixedrange=True,
            ),
            annotations=etiquetas_anotaciones
            + [
                dict(
                    text="NORTE ◀",
                    xref="paper",
                    yref="paper",
                    x=0.01,
                    y=0.01,
                    showarrow=False,
                    font=dict(size=10, color="#77708C"),
                ),
                dict(
                    text="▶ SUR",
                    xref="paper",
                    yref="paper",
                    x=0.99,
                    y=0.01,
                    showarrow=False,
                    font=dict(size=10, color="#77708C"),
                ),
            ],
            paper_bgcolor="white",
            plot_bgcolor="white",
            autosize=True,
            font=dict(family="Segoe UI, Arial, sans-serif", size=11),
        )

        if region_sel == "Nacional":
            S_curr, I_curr, R_curr, N_curr, titulo_curva = (
                S_nac,
                I_nac,
                R_nac,
                N_total,
                "Evolución nacional (Chile)",
            )
        else:
            idx_r = REGIONES_ORDENADAS.index(region_sel)
            S_curr, I_curr, R_curr, N_curr, titulo_curva = (
                S_mat[idx_r, :],
                I_mat[idx_r, :],
                R_mat[idx_r, :],
                POBLACIONES[region_sel],
                f"Región de {region_sel}",
            )

        fig_curvas = go.Figure()
        for serie, etiqueta, color, grosor in [
            (S_curr, "Susceptibles (S)", "#3B82F6", 2.6),
            (I_curr, "Infectados (I)", "#EC4899", 2.9),
            (R_curr, "Recuperados (R)", "#14B8A6", 2.6),
        ]:
            fig_curvas.add_trace(
                go.Scatter(
                    x=t,
                    y=serie / N_curr * 100,
                    name=etiqueta,
                    mode="lines",
                    line=dict(color=color, width=grosor),
                )
            )
        fig_curvas.update_layout(
            title=dict(
                text=titulo_curva,
                font=dict(size=15, color="#24204A"),
                x=0.04,
                xanchor="left",
            ),
            xaxis=dict(
                title=dict(text="Días", standoff=15),
                range=[0, 180],
                dtick=20,
                gridcolor="#EDF0F7",
                zeroline=False,
                fixedrange=True,
                ticks="outside",
                ticklen=4,
                tickcolor="#C9CCE0",
            ),
            yaxis=dict(
                title=dict(text="% de población", standoff=10),
                gridcolor="#EDF0F7",
                range=[0, 102],
                dtick=20,
                fixedrange=True,
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11),
            ),
            margin=dict(l=65, r=22, t=67, b=62),
            paper_bgcolor="white",
            plot_bgcolor="white",
            autosize=True,
            font=dict(family="Segoe UI, Arial, sans-serif", size=11, color="#283148"),
        )

        fig_hm = go.Figure(
            data=go.Heatmap(
                z=I_mat / N_VEC[:, None] * 100.0,
                x=t,
                y=REGIONES_ORDENADAS,
                colorscale="Purples",
                colorbar=dict(
                    thickness=13,
                    len=0.82,
                    y=0.5,
                    yanchor="middle",
                    title=dict(text="% Inf.", font=dict(size=10)),
                ),
                hovertemplate=(
                    "Día: %{x}<br>Región: %{y}<br>Infectados: %{z:.2f}%<extra></extra>"
                ),
            )
        )
        fig_hm.update_layout(
            title=dict(
                text="Propagación espacio-temporal regional",
                font=dict(size=15, color="#24204A"),
                x=0.04,
                xanchor="left",
            ),
            xaxis=dict(
                title=dict(text="Días", standoff=15),
                range=[0, 180],
                dtick=30,
                showgrid=False,
                fixedrange=True,
            ),
            yaxis=dict(
                autorange="reversed",
                showgrid=False,
                fixedrange=True,
                tickmode="array",
                tickvals=REGIONES_ORDENADAS,
                ticktext=REGIONES_ORDENADAS,
                tickfont=dict(size=10),
                automargin=True,
            ),
            margin=dict(l=167, r=65, t=60, b=60),
            paper_bgcolor="white",
            plot_bgcolor="white",
            autosize=True,
            font=dict(family="Segoe UI, Arial, sans-serif", size=11),
        )

        # Los resultados inferiores corresponden a la region seleccionada y al dia.
        porcentaje_s = float(S_curr[dia_idx] / N_curr * 100.0)
        porcentaje_i = float(I_curr[dia_idx] / N_curr * 100.0)
        porcentaje_r = float(R_curr[dia_idx] / N_curr * 100.0)
        alcance = "Chile" if region_sel == "Nacional" else f"la región de {region_sel}"
        interpretacion = (
            f"En {alcance}, "
            f"al día {dia_idx}, el {porcentaje_i:.1f}% de la población "
            "se encuentra en el compartimento infectado del modelo. "
            "El resultado es un escenario simulado, no una cifra epidemiológica real."
        )

        figura_activa = {
            "tab-curvas": fig_curvas,
            "tab-grafo": fig_grafo,
            "tab-heatmap": fig_hm,
        }.get(pestana, fig_curvas)

        return (
            str_r0,
            desc_r0,
            str_imax,
            str_tmax,
            str_rebano,
            figura_activa,
            f"{porcentaje_s:.1f}%",
            f"{porcentaje_i:.1f}%",
            f"{porcentaje_r:.1f}%",
            f"Día {dia_idx} · {region_sel}",
            interpretacion,
        )
