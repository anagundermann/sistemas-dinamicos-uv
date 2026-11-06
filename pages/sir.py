"""
Sistemas Dinámicos UV: Laboratorio Modelo SIR en Grafos aplicados a COVID-19 en Chile.
Optimizado para garantizar la carga correcta de datos, modales emergentes y visualización fluida.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import networkx as nx

from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from components.modal_supuestos_sir import (
    crear_boton_supuestos_sir,
    crear_modal_supuestos_sir,
    registrar_callbacks_supuestos_sir,
)

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

COORDS = {
    "Arica y Parinacota": (-70.30, -18.47),
    "Tarapacá": (-69.35, -20.21),
    "Antofagasta": (-70.40, -23.65),
    "Atacama": (-70.33, -27.36),
    "Coquimbo": (-71.33, -29.95),
    "Valparaíso": (-71.61, -33.04),
    "Metropolitana": (-70.66, -33.44),
    "O’Higgins": (-70.98, -34.58),
    "Maule": (-71.65, -35.42),
    "Ñuble": (-72.10, -36.60),
    "Biobío": (-73.04, -36.82),
    "Araucanía": (-72.59, -38.73),
    "Los Ríos": (-73.24, -39.81),
    "Los Lagos": (-72.94, -41.47),
    "Aysén": (-72.06, -45.57),
    "Magallanes": (-70.91, -53.16),
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
# 2. DISEÑO DE LA PÁGINA (LAYOUT)
# --------------------------------------------------


def crear_pagina():
    r0_inicial = 0.30 / 0.10
    return html.Div(
        className="sd-grid",
        style={"gap": "10px"},
        children=[
            # Barra superior con modales explicativos
            html.Section(
                className="sd-tarjeta",
                style={
                    "padding": "8px 14px",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                },
                children=[
                    html.Span(
                        "🔬 Laboratorio COVID-19 en Redes de Chile",
                        style={
                            "fontWeight": "800",
                            "color": "#1E1B4B",
                            "fontSize": "1.05rem",
                        },
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "10px",
                            "flexWrap": "wrap",
                            "justifyContent": "flex-end",
                        },
                        children=[
                            html.Button(
                                "📖 ¿Qué es el Modelo SIR?",
                                id="btn-abrir-modal-sir",
                                n_clicks=0,
                                className="sd-inicio",
                                style={
                                    "fontSize": "0.85rem",
                                    "padding": "5px 10px",
                                    "cursor": "pointer",
                                },
                            ),
                            html.Button(
                                "📐 Modelo Matemático",
                                id="btn-abrir-modal-mat",
                                n_clicks=0,
                                className="sd-inicio",
                                style={
                                    "fontSize": "0.85rem",
                                    "padding": "5px 10px",
                                    "cursor": "pointer",
                                },
                            ),
                            crear_boton_supuestos_sir(),
                        ],
                    ),
                ],
            ),
            # Modal 1: Definición SIR
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Definición: Modelo SIR en Redes Complejas"),
                        style={"color": "#1E1B4B", "fontWeight": "800"},
                    ),
                    dbc.ModalBody(
                        children=[
                            html.P(
                                "El modelo epidemiológico SIR clásico divide a una población homogénea en tres estados: Susceptibles (S), Infectados (I) y Recuperados (R)."
                            ),
                            html.P(
                                "Este laboratorio utiliza un grafo hipotético que conecta las 16 regiones de Chile. Sus conexiones representan contactos de transmisión entre regiones, no flujos reales de personas medidos."
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Cerrar",
                            id="btn-cerrar-modal-sir",
                            className="ms-auto",
                            n_clicks=0,
                            style={
                                "backgroundColor": "#7C3AED",
                                "color": "white",
                                "border": "none",
                            },
                        )
                    ),
                ],
                id="modal-sir",
                is_open=False,
                centered=True,
            ),
            # Modal 2: Matemáticas
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Modelo Matemático y Variables"),
                        style={"color": "#1E1B4B", "fontWeight": "800"},
                    ),
                    dbc.ModalBody(
                        children=[
                            html.Div(
                                dcc.Markdown(
                                    r"$$\begin{aligned}"
                                    r"\frac{dS_i}{dt}&=-\beta\frac{S_iI_i}{N_i}-\alpha S_i\sum_j A_{ij}\frac{I_j}{N_j}\\"
                                    r"\frac{dI_i}{dt}&=\beta\frac{S_iI_i}{N_i}+\alpha S_i\sum_j A_{ij}\frac{I_j}{N_j}-\gamma I_i\\"
                                    r"\frac{dR_i}{dt}&=\gamma I_i"
                                    r"\end{aligned}$$",
                                    mathjax=True,
                                ),
                                className="sd-formula",
                            ),
                            html.P(
                                "Sᵢ, Iᵢ, Rᵢ: susceptibles, infectados y recuperados; Nᵢ: población regional; β: infección local; γ: recuperación; α: transmisión asociada a las conexiones de la red."
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Cerrar",
                            id="btn-cerrar-modal-mat",
                            className="ms-auto",
                            n_clicks=0,
                            style={
                                "backgroundColor": "#7C3AED",
                                "color": "white",
                                "border": "none",
                            },
                        )
                    ),
                ],
                id="modal-mat",
                is_open=False,
                centered=True,
                size="lg",
            ),
            # Modal 3: Supuestos, datos y limitaciones
            crear_modal_supuestos_sir(),
            # KPIs de Resumen
            html.Div(
                className="sd-grid sd-grid-tres",
                style={"gap": "8px"},
                children=[
                    html.Div(
                        className="sd-tarjeta sd-tarjeta-resultado",
                        style={"padding": "8px"},
                        children=[
                            html.Span(
                                "β/γ · referencia local",
                                className="sd-lab-detalle",
                                style={"fontSize": "0.75rem"},
                            ),
                            html.H3(
                                id="sir-kpi-r0",
                                children=f"{r0_inicial:.2f}",
                                style={
                                    "fontSize": "1.1rem",
                                    "margin": "2px 0",
                                    "color": "#1E1B4B",
                                },
                            ),
                            html.P(
                                id="sir-kpi-r0-desc",
                                children="--",
                                style={
                                    "fontSize": "0.7rem",
                                    "margin": "0",
                                    "color": "#625E7C",
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        className="sd-tarjeta sd-tarjeta-resultado",
                        style={"padding": "8px"},
                        children=[
                            html.Span(
                                "Pico Máx. (I_max)",
                                className="sd-lab-detalle",
                                style={"fontSize": "0.75rem"},
                            ),
                            html.H3(
                                id="sir-kpi-imax",
                                children="--",
                                style={
                                    "fontSize": "1.1rem",
                                    "margin": "2px 0",
                                    "color": "#1E1B4B",
                                },
                            ),
                            html.P(
                                id="sir-kpi-tmax",
                                children="--",
                                style={
                                    "fontSize": "0.7rem",
                                    "margin": "0",
                                    "color": "#625E7C",
                                },
                            ),
                        ],
                    ),
                    html.Div(
                        className="sd-tarjeta sd-tarjeta-resultado",
                        style={"padding": "8px"},
                        children=[
                            html.Span(
                                "Umbral teórico sin red",
                                className="sd-lab-detalle",
                                style={"fontSize": "0.75rem"},
                            ),
                            html.H3(
                                id="sir-kpi-rebaño",
                                children="--",
                                style={
                                    "fontSize": "1.1rem",
                                    "margin": "2px 0",
                                    "color": "#1E1B4B",
                                },
                            ),
                            html.P(
                                "Referencia del SIR homogéneo",
                                style={
                                    "fontSize": "0.7rem",
                                    "margin": "0",
                                    "color": "#625E7C",
                                },
                            ),
                        ],
                    ),
                ],
            ),
            # Controles Interactivos
            html.Section(
                className="sd-tarjeta sd-tarjeta-controles",
                style={"padding": "10px 14px"},
                children=[
                    html.H3(
                        "Controles de Parámetros Epidémicos y Conectividad",
                        className="sd-titulo-tarjeta",
                        style={"fontSize": "0.95rem", "marginBottom": "6px"},
                    ),
                    html.Div(
                        className="sd-grid sd-grid-dos",
                        style={"gap": "14px"},
                        children=[
                            html.Div(
                                [
                                    html.Label(
                                        "Tasa Infección (β) / Recuperación (γ) / Movilidad (α):",
                                        style={
                                            "fontWeight": "650",
                                            "color": "#1E1B4B",
                                            "fontSize": "0.8rem",
                                        },
                                    ),
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "gap": "8px",
                                            "marginTop": "2px",
                                        },
                                        children=[
                                            html.Div(
                                                style={"flex": 1},
                                                children=[
                                                    html.Span(
                                                        "β:",
                                                        style={"fontSize": "0.75rem"},
                                                    ),
                                                    dcc.Slider(
                                                        id="sir-slider-beta",
                                                        min=0.05,
                                                        max=0.80,
                                                        step=0.01,
                                                        value=0.30,
                                                        marks={
                                                            0.1: "0.1",
                                                            0.4: "0.4",
                                                            0.8: "0.8",
                                                        },
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                style={"flex": 1},
                                                children=[
                                                    html.Span(
                                                        "γ:",
                                                        style={"fontSize": "0.75rem"},
                                                    ),
                                                    dcc.Slider(
                                                        id="sir-slider-gamma",
                                                        min=0.02,
                                                        max=0.40,
                                                        step=0.01,
                                                        value=0.10,
                                                        marks={
                                                            0.05: "0.05",
                                                            0.2: "0.2",
                                                            0.4: "0.4",
                                                        },
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Span(
                                        "α (Transmisión entre regiones):",
                                        style={
                                            "fontSize": "0.75rem",
                                            "marginTop": "4px",
                                            "display": "block",
                                        },
                                    ),
                                    dcc.Slider(
                                        id="sir-slider-alpha",
                                        min=0.00,
                                        max=0.15,
                                        step=0.005,
                                        value=0.03,
                                        marks={
                                            0.0: "Aislado",
                                            0.07: "Medio",
                                            0.15: "Alto",
                                        },
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        style={"display": "flex", "gap": "8px"},
                                        children=[
                                            html.Div(
                                                style={"flex": 1},
                                                children=[
                                                    html.Label(
                                                        "Región Semilla (I₀):",
                                                        style={
                                                            "fontWeight": "650",
                                                            "color": "#1E1B4B",
                                                            "fontSize": "0.8rem",
                                                        },
                                                    ),
                                                    dcc.Dropdown(
                                                        id="sir-drop-semilla",
                                                        options=[
                                                            {"label": r, "value": r}
                                                            for r in REGIONES_ORDENADAS
                                                        ],
                                                        value="Metropolitana",
                                                        clearable=False,
                                                        style={"fontSize": "0.8rem"},
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                style={"flex": 1},
                                                children=[
                                                    html.Label(
                                                        "Foco Región:",
                                                        style={
                                                            "fontWeight": "650",
                                                            "color": "#1E1B4B",
                                                            "fontSize": "0.8rem",
                                                        },
                                                    ),
                                                    dcc.Dropdown(
                                                        id="sir-drop-region",
                                                        options=[
                                                            {
                                                                "label": "Nacional",
                                                                "value": "Nacional",
                                                            }
                                                        ]
                                                        + [
                                                            {"label": r, "value": r}
                                                            for r in REGIONES_ORDENADAS
                                                        ],
                                                        value="Nacional",
                                                        clearable=False,
                                                        style={"fontSize": "0.8rem"},
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Label(
                                        "Día a Inspeccionar en el Grafo:",
                                        style={
                                            "fontWeight": "650",
                                            "color": "#1E1B4B",
                                            "fontSize": "0.8rem",
                                            "marginTop": "6px",
                                            "display": "block",
                                        },
                                    ),
                                    dcc.Slider(
                                        id="sir-slider-dia-grafo",
                                        min=0,
                                        max=180,
                                        step=1,
                                        value=45,
                                        marks={0: "Día 0", 90: "90", 180: "180"},
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
            # GRÁFICOS VISIBLES DIRECTAMENTE (Sin sub-pestañas para evitar errores de renderizado)
            html.Div(
                className="sd-grid sd-grid-dos",
                style={"gap": "10px"},
                children=[
                    html.Section(
                        className="sd-tarjeta sd-tarjeta-grafico",
                        style={"padding": "10px"},
                        children=[
                            html.H3(
                                "🌐 Grafo Espacial de Chile",
                                className="sd-titulo-tarjeta",
                                style={"fontSize": "0.95rem", "marginBottom": "4px"},
                            ),
                            dcc.Graph(
                                id="sir-grafico-grafo",
                                style={"height": "300px"},
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                    html.Section(
                        className="sd-tarjeta sd-tarjeta-grafico",
                        style={"padding": "10px"},
                        children=[
                            html.H3(
                                "📈 Curvas temporales S-I-R (simulación)",
                                className="sd-titulo-tarjeta",
                                style={"fontSize": "0.95rem", "marginBottom": "4px"},
                            ),
                            dcc.Graph(
                                id="sir-grafico-curvas",
                                style={"height": "300px"},
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="sd-tarjeta sd-tarjeta-grafico",
                style={"padding": "10px"},
                children=[
                    html.H3(
                        "🗺️ Matriz Espacio-Temporal de Propagación Regional",
                        className="sd-titulo-tarjeta",
                        style={"fontSize": "0.95rem", "marginBottom": "4px"},
                    ),
                    dcc.Graph(
                        id="sir-grafico-heatmap",
                        style={"height": "250px"},
                        config={"displayModeBar": False},
                    ),
                ],
            ),
        ],
    )


# --------------------------------------------------
# 3. REGISTRO DE CALLBACKS DEL MODELO SIR
# --------------------------------------------------


def registrar_callbacks(app):
    registrar_callbacks_supuestos_sir(app)

    @app.callback(
        Output("modal-sir", "is_open"),
        [
            Input("btn-abrir-modal-sir", "n_clicks"),
            Input("btn-cerrar-modal-sir", "n_clicks"),
        ],
        [State("modal-sir", "is_open")],
    )
    def toggle_modal_sir(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output("modal-mat", "is_open"),
        [
            Input("btn-abrir-modal-mat", "n_clicks"),
            Input("btn-cerrar-modal-mat", "n_clicks"),
        ],
        [State("modal-mat", "is_open")],
    )
    def toggle_modal_mat(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output("sir-kpi-r0", "children"),
        Output("sir-kpi-r0-desc", "children"),
        Output("sir-kpi-imax", "children"),
        Output("sir-kpi-tmax", "children"),
        Output("sir-kpi-rebaño", "children"),
        Output("sir-grafico-grafo", "figure"),
        Output("sir-grafico-curvas", "figure"),
        Output("sir-grafico-heatmap", "figure"),
        Input("sir-slider-beta", "value"),
        Input("sir-slider-gamma", "value"),
        Input("sir-slider-alpha", "value"),
        Input("sir-drop-semilla", "value"),
        Input("sir-drop-region", "value"),
        Input("sir-slider-dia-grafo", "value"),
    )
    def actualizar_laboratorio_sir(beta, gamma, alpha, semilla, region_sel, dia_grafo):
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
        i_max_val = (I_nac[idx_pico] / N_total) * 100.0
        t_max_val = t[idx_pico]

        str_rebano = f"{(1.0 - 1.0 / r0) * 100.0:.1f}%" if r0 > 1.0 else "N/A"
        str_imax = f"{i_max_val:.2f}%"
        str_tmax = f"Día {int(t_max_val)}"

        dia_idx = min(max(int(45 if dia_grafo is None else dia_grafo), 0), dias)
        I_dia = I_mat[:, dia_idx]
        prevalencia_dia = (I_dia / N_VEC) * 100.0

        edge_x, edge_y = [], []
        for edge in GRAFO_CHILE.edges():
            x0, y0 = COORDS[edge[0]]
            x1, y1 = COORDS[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        trace_edges = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1.5, color="#CBD5E1"),
            hoverinfo="none",
            mode="lines",
        )

        node_x = [COORDS[r][0] for r in REGIONES_ORDENADAS]
        node_y = [COORDS[r][1] for r in REGIONES_ORDENADAS]
        node_hover = [
            f"<b>{r}</b><br>Infectados: {int(I_dia[i]):,}<br>Prevalencia: {prevalencia_dia[i]:.2f}%"
            for i, r in enumerate(REGIONES_ORDENADAS)
        ]

        trace_nodes = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=[r.split()[0] for r in REGIONES_ORDENADAS],
            textposition="top center",
            hovertext=node_hover,
            hoverinfo="text",
            marker=dict(
                showscale=True,
                colorscale="Purples",
                color=prevalencia_dia,
                size=[
                    max(10, int(np.sqrt(POBLACIONES[r]) / 90))
                    for r in REGIONES_ORDENADAS
                ],
                colorbar=dict(
                    thickness=10,
                    title=dict(text="% Inf.", font=dict(size=9, color="#1E1B4B")),
                ),
                line=dict(width=1, color="#FFFFFF"),
            ),
        )

        fig_grafo = go.Figure(data=[trace_edges, trace_nodes])
        fig_grafo.update_layout(
            title=dict(
                text=f"Red de Chile — Día {dia_idx}",
                font=dict(size=12, color="#1E1B4B"),
            ),
            margin=dict(l=10, r=10, t=25, b=10),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        fig_curvas = go.Figure()
        if region_sel == "Nacional":
            S_curr, I_curr, R_curr, N_curr, titulo_curva = (
                S_nac,
                I_nac,
                R_nac,
                N_total,
                "Evolución Nacional (Chile)",
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

        fig_curvas.add_trace(
            go.Scatter(
                x=t,
                y=S_curr / N_curr * 100,
                mode="lines",
                name="Susceptibles (S)",
                line=dict(color="#3B82F6", width=2),
            )
        )
        fig_curvas.add_trace(
            go.Scatter(
                x=t,
                y=I_curr / N_curr * 100,
                mode="lines",
                name="Infectados (I)",
                line=dict(color="#EC4899", width=2.5),
            )
        )
        fig_curvas.add_trace(
            go.Scatter(
                x=t,
                y=R_curr / N_curr * 100,
                mode="lines",
                name="Recuperados (R)",
                line=dict(color="#14B8A6", width=2),
            )
        )

        fig_curvas.update_layout(
            title=dict(text=titulo_curva, font=dict(size=12, color="#1E1B4B")),
            xaxis=dict(title="Días", gridcolor="#F1F5F9"),
            yaxis=dict(title="% Población", gridcolor="#F1F5F9"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=9),
            ),
            margin=dict(l=25, r=10, t=30, b=25),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        fig_hm = go.Figure(
            data=go.Heatmap(
                z=(I_mat / N_VEC[:, None]) * 100.0,
                x=t,
                y=REGIONES_ORDENADAS,
                colorscale="Purples",
                colorbar=dict(
                    title=dict(text="% Inf.", font=dict(size=9, color="#1E1B4B"))
                ),
            )
        )
        fig_hm.update_layout(
            title=dict(
                text="Propagación Espacio-Temporal Regional",
                font=dict(size=12, color="#1E1B4B"),
            ),
            xaxis=dict(title="Días"),
            yaxis=dict(autorange="reversed", tickfont=dict(size=8)),
            margin=dict(l=90, r=10, t=25, b=25),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        return (
            str_r0,
            desc_r0,
            str_imax,
            str_tmax,
            str_rebano,
            fig_grafo,
            fig_curvas,
            fig_hm,
        )
