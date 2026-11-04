"""Laboratorio interactivo de depredador-presa (Lotka-Volterra)."""

from dash import Input, Output, dcc, html
import plotly.graph_objects as go

from models.modelo_lotka_volterra import (
    calcular_equilibrio,
    simular_lotka_volterra,
)


COLOR_PRESAS = "#14B8A6"
COLOR_DEPREDADORES = "#7C3AED"


def crear_control(titulo, control_id, minimo, maximo, paso, valor, marcas):
    return html.Div(
        className="sd-control-lv",
        children=[
            html.Label(titulo, className="sd-lab-detalle"),
            dcc.Slider(
                id=control_id,
                min=minimo,
                max=maximo,
                step=paso,
                value=valor,
                marks=marcas,
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ],
        style={"paddingBottom": "12px"},
    )


def crear_pagina():
    return html.Div(
        className="sd-grid",
        children=[
            html.Section(
                className="sd-tarjeta sd-tarjeta-matematica",
                children=[
                    html.H2(
                        "Depredador–Presa · Lotka–Volterra",
                        className="sd-titulo-seccion",
                    ),
                    html.P(
                        "Explora cómo interactúan dos poblaciones: las presas crecen "
                        "en ausencia de depredadores y estos dependen de las presas "
                        "para reproducirse.",
                        className="sd-portada-descripcion",
                    ),
                    html.Div(
                        dcc.Markdown(
                            r"$$\begin{aligned}"
                            r"\dot{x}&=\alpha x-\beta xy\\"
                            r"\dot{y}&=\delta xy-\gamma y"
                            r"\end{aligned}$$",
                            mathjax=True,
                        ),
                        className="sd-formula",
                        style={"overflow": "visible"},
                    ),
                    html.P(
                        "x: presas · y: depredadores · t: tiempo. "
                        "Las poblaciones son valores teóricos del modelo.",
                        className="sd-lab-detalle",
                    ),
                ],
            ),
            html.Section(
                className="sd-tarjeta sd-tarjeta-controles",
                children=[
                    html.H3(
                        "Experimenta con los parámetros", className="sd-titulo-tarjeta"
                    ),
                    html.Div(
                        className="sd-grid sd-grid-dos",
                        children=[
                            html.Div(
                                children=[
                                    crear_control(
                                        "α · Crecimiento de presas",
                                        "lv-alpha",
                                        0.1,
                                        1.2,
                                        0.05,
                                        0.65,
                                        {0.1: "0.1", 0.65: "0.65", 1.2: "1.2"},
                                    ),
                                    crear_control(
                                        "β · Intensidad de depredación",
                                        "lv-beta",
                                        0.005,
                                        0.05,
                                        0.001,
                                        0.018,
                                        {0.005: "0.005", 0.025: "0.025", 0.05: "0.05"},
                                    ),
                                    crear_control(
                                        "γ · Mortalidad de depredadores",
                                        "lv-gamma",
                                        0.1,
                                        1.0,
                                        0.05,
                                        0.55,
                                        {0.1: "0.1", 0.55: "0.55", 1.0: "1.0"},
                                    ),
                                ]
                            ),
                            html.Div(
                                children=[
                                    crear_control(
                                        "δ · Reproducción por depredación",
                                        "lv-delta",
                                        0.005,
                                        0.04,
                                        0.001,
                                        0.012,
                                        {0.005: "0.005", 0.02: "0.02", 0.04: "0.04"},
                                    ),
                                    crear_control(
                                        "Presas iniciales",
                                        "lv-presas-0",
                                        10,
                                        120,
                                        5,
                                        60,
                                        {10: "10", 60: "60", 120: "120"},
                                    ),
                                    crear_control(
                                        "Depredadores iniciales",
                                        "lv-depredadores-0",
                                        5,
                                        100,
                                        5,
                                        20,
                                        {5: "5", 50: "50", 100: "100"},
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="sd-grid sd-grid-dos",
                children=[
                    html.Section(
                        className="sd-tarjeta sd-tarjeta-grafico",
                        children=[
                            html.H3(
                                "Evolución de las poblaciones",
                                className="sd-titulo-tarjeta",
                            ),
                            dcc.Graph(
                                id="lv-grafico-tiempo",
                                config={
                                    "displayModeBar": False,
                                    "scrollZoom": False,
                                    "responsive": True,
                                },
                                style={
                                    "height": "clamp(270px, 40vh, 350px)",
                                    "width": "100%",
                                },
                            ),
                        ],
                    ),
                    html.Section(
                        className="sd-tarjeta sd-tarjeta-grafico",
                        children=[
                            html.H3("Plano de fases", className="sd-titulo-tarjeta"),
                            dcc.Graph(
                                id="lv-grafico-fases",
                                config={
                                    "displayModeBar": False,
                                    "scrollZoom": False,
                                    "responsive": True,
                                },
                                style={
                                    "height": "clamp(270px, 40vh, 350px)",
                                    "width": "100%",
                                },
                            ),
                        ],
                    ),
                ],
            ),
            html.Section(
                className="sd-tarjeta sd-tarjeta-resultado",
                children=[
                    html.H3(
                        "¿Qué nos dicen los gráficos?", className="sd-titulo-tarjeta"
                    ),
                    html.Div(id="lv-lectura", className="sd-modal-texto"),
                ],
            ),
        ],
    )


def registrar_callbacks(app):
    @app.callback(
        Output("lv-grafico-tiempo", "figure"),
        Output("lv-grafico-fases", "figure"),
        Output("lv-lectura", "children"),
        Input("lv-alpha", "value"),
        Input("lv-beta", "value"),
        Input("lv-gamma", "value"),
        Input("lv-delta", "value"),
        Input("lv-presas-0", "value"),
        Input("lv-depredadores-0", "value"),
    )
    def actualizar_laboratorio(alpha, beta, gamma, delta, presas_0, depredadores_0):
        tiempos, presas, depredadores = simular_lotka_volterra(
            alpha, beta, gamma, delta, presas_0, depredadores_0
        )
        presas_eq, depredadores_eq = calcular_equilibrio(alpha, beta, gamma, delta)

        figura_tiempo = go.Figure()
        figura_tiempo.add_trace(
            go.Scatter(
                x=tiempos,
                y=presas,
                mode="lines",
                name="Presas",
                line={"color": COLOR_PRESAS, "width": 3},
            )
        )
        figura_tiempo.add_trace(
            go.Scatter(
                x=tiempos,
                y=depredadores,
                mode="lines",
                name="Depredadores",
                line={"color": COLOR_DEPREDADORES, "width": 3},
            )
        )
        figura_tiempo.update_layout(
            margin={"l": 45, "r": 15, "t": 20, "b": 45},
            xaxis_title="Tiempo",
            yaxis_title="Población (unidades del modelo)",
            hovermode="x unified",
            dragmode=False,
            legend={"orientation": "h", "y": 1.13, "x": 0},
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        figura_fases = go.Figure()
        figura_fases.add_trace(
            go.Scatter(
                x=presas,
                y=depredadores,
                mode="lines",
                name="Trayectoria",
                line={"color": COLOR_DEPREDADORES, "width": 3},
            )
        )
        figura_fases.add_trace(
            go.Scatter(
                x=[presas_0],
                y=[depredadores_0],
                mode="markers",
                name="Inicio",
                marker={"color": COLOR_PRESAS, "size": 11},
            )
        )
        figura_fases.add_trace(
            go.Scatter(
                x=[presas_eq],
                y=[depredadores_eq],
                mode="markers",
                name="Equilibrio",
                marker={"color": "#F59E0B", "symbol": "x", "size": 12},
            )
        )
        figura_fases.update_layout(
            margin={"l": 45, "r": 15, "t": 20, "b": 45},
            xaxis_title="Presas (x)",
            yaxis_title="Depredadores (y)",
            dragmode=False,
            legend={"orientation": "h", "y": 1.13, "x": 0},
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        lectura = html.Div(
            children=[
                html.P(
                    [
                        html.Strong("Equilibrio de coexistencia: "),
                        f"x* = {presas_eq:.1f} presas; y* = {depredadores_eq:.1f} depredadores.",
                    ]
                ),
                html.P(
                    "En este modelo idealizado, las poblaciones pueden oscilar "
                    "alrededor del equilibrio. El gráfico temporal muestra cómo "
                    "cambian; el plano de fases muestra la trayectoria (x(t), y(t))."
                ),
                html.P(
                    "Prueba cambiar solo un parámetro y observa qué ocurre "
                    "con el equilibrio y la forma de las oscilaciones."
                ),
            ]
        )
        return figura_tiempo, figura_fases, lectura
