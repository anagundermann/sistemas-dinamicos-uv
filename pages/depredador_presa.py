"""Laboratorio interactivo de depredador-presa (Lotka-Volterra).

La presentacion de esta pagina se controla en assets/zz-depredador-presa.css.
Se mantienen los seis parametros y los identificadores de los callbacks originales.
"""

from components.barra_animacion_lv import crear_barra_animacion_vista_previa
from dash import Input, Output, State, ctx, dcc, get_asset_url, html, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from components.ecosistema_lv import (
    crear_contenido_ecosistema,
    registrar_callbacks_ecosistema,
)

from components.modelo_matematico_lv import crear_contenido_modelo_matematico

from components.analisis_sistema_lv import crear_contenido_analisis_sistema

from models.modelo_lotka_volterra import (
    calcular_equilibrio,
    simular_lotka_volterra,
)


COLOR_PRESAS = "#14B8A6"
COLOR_DEPREDADORES = "#7C3AED"


# Configuracion separada para editar los controles sin tocar el layout.
CONTROLES = [
    ("α · Crecimiento de presas", "lv-alpha", 0.1, 1.2, 0.05, 0.65),
    ("β · Intensidad de depredación", "lv-beta", 0.005, 0.05, 0.001, 0.018),
    ("γ · Mortalidad de depredadores", "lv-gamma", 0.1, 1.0, 0.05, 0.55),
    ("δ · Reproducción por depredación", "lv-delta", 0.005, 0.04, 0.001, 0.012),
    ("Presas iniciales", "lv-presas-0", 10, 120, 5, 60),
    ("Depredadores iniciales", "lv-depredadores-0", 5, 100, 5, 20),
]


def crear_control(titulo, control_id, minimo, maximo, paso, valor):
    """Control compacto: etiqueta y valor arriba, deslizador debajo."""
    return html.Div(
        className="lv-control",
        children=[
            html.Div(
                className="lv-control-encabezado",
                children=[
                    html.Label(titulo, className="lv-control-etiqueta"),
                    html.Output(
                        id=f"{control_id}-valor",
                        children=f"{valor:g}",
                        className="lv-control-valor",
                    ),
                ],
            ),
            dcc.Slider(
                id=control_id,
                min=minimo,
                max=maximo,
                step=paso,
                value=valor,
                marks={minimo: f"{minimo:g}", maximo: f"{maximo:g}"},
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ],
    )


def crear_grafico(titulo, grafico_id):
    return html.Section(
        className="sd-tarjeta sd-tarjeta-grafico lv-tarjeta-grafico",
        children=[
            html.H3(titulo, className="sd-titulo-tarjeta"),
            dcc.Graph(
                id=grafico_id,
                className="lv-grafico",
                config={
                    "displayModeBar": False,
                    "scrollZoom": False,
                    "responsive": True,
                },
            ),
        ],
    )


def crear_pagina():
    return html.Div(
        className="lv-pagina",
        children=[
            html.Header(
                className="lv-cabecera",
                children=[
                    html.H2(
                        "Depredador–Presa · Lotka–Volterra",
                        className="sd-titulo-seccion lv-titulo",
                    ),
                    html.Div(
                        className="lv-cabecera-siluetas",
                        children=[
                            html.Img(
                                src=get_asset_url("zorro-lineal.svg"),
                                alt="",
                                className="lv-silueta-zorro",
                            ),
                            html.Img(
                                src=get_asset_url("conejo-lineal.svg"),
                                alt="",
                                className="lv-silueta-conejo",
                            ),
                        ],
                    ),
                    html.Div(
                        className="lv-botones-info",
                        children=[
                            dbc.Button(
                                "Ecosistema",
                                id="lv-boton-modelo",
                                className="lv-boton-info",
                                n_clicks=0,
                            ),
                            dbc.Button(
                                "Modelo matemático",
                                id="lv-boton-ecuaciones",
                                className="lv-boton-info",
                                n_clicks=0,
                            ),
                            dbc.Button(
                                "Análisis del sistema",
                                id="lv-boton-variables",
                                className="lv-boton-info",
                                n_clicks=0,
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="lv-distribucion",
                children=[
                    html.Section(
                        className="sd-tarjeta sd-tarjeta-controles lv-panel-controles",
                        children=[
                            html.H3(
                                "Experimenta con los parámetros",
                                className="sd-titulo-tarjeta",
                            ),
                            html.Div(
                                className="lv-lista-controles",
                                children=[crear_control(*datos) for datos in CONTROLES],
                            ),
                        ],
                    ),
                    html.Div(
                        className="lv-panel-derecho",
                        children=[
                            html.Div(
                                className="lv-panel-graficos",
                                children=[
                                    crear_grafico(
                                        "Evolución de las poblaciones",
                                        "lv-grafico-tiempo",
                                    ),
                                    crear_grafico("Plano de fases", "lv-grafico-fases"),
                                ],
                            ),
                            html.Section(
                                className="sd-tarjeta sd-tarjeta-resultado lv-panel-resultados",
                                children=[
                                    html.Div(
                                        id="lv-lectura", className="sd-modal-texto"
                                    ),
                                    crear_barra_animacion_vista_previa(),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            dbc.Modal(
                id="lv-modal-informacion",
                is_open=False,
                centered=True,
                size="xl",
                className="lv-modal",
                children=[
                    dbc.ModalHeader(dbc.ModalTitle(id="lv-modal-titulo")),
                    dbc.ModalBody(id="lv-modal-cuerpo"),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Cerrar", id="lv-cerrar-modal", className="lv-boton-cerrar"
                        )
                    ),
                ],
            ),
        ],
    )


def contenido_modal(seccion):
    """Contenido de ayuda sin ocupar espacio en el laboratorio."""
    if seccion == "modelo":
        return "Ecosistema · Zorros y conejos", crear_contenido_ecosistema()
    if seccion == "ecuaciones":
        return "Modelo matemático · Lotka–Volterra", crear_contenido_modelo_matematico()
    return "Análisis del sistema · Lotka–Volterra", crear_contenido_analisis_sistema()


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
            # Espacio real para titulos y numeros de los dos ejes.
            margin={"l": 70, "r": 18, "t": 35, "b": 78},
            xaxis={
                "title": {"text": "Tiempo", "standoff": 14},
                "automargin": True,
            },
            yaxis={
                "title": {"text": "Población (unidades del modelo)", "standoff": 12},
                "automargin": True,
            },
            hovermode="x unified",
            dragmode=False,
            legend={"orientation": "h", "y": 1.12, "x": 0},
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
            margin={"l": 70, "r": 18, "t": 35, "b": 78},
            xaxis={
                "title": {"text": "Presas (x)", "standoff": 14},
                "automargin": True,
            },
            yaxis={
                "title": {"text": "Depredadores (y)", "standoff": 12},
                "automargin": True,
            },
            dragmode=False,
            legend={"orientation": "h", "y": 1.12, "x": 0},
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        lectura = html.Div(
            className="lv-resumen",
            children=[
                html.Div(
                    className="lv-equilibrio-recuadro",
                    children=[
                        html.Div(
                            "Equilibrio de coexistencia",
                            className="lv-equilibrio-titulo",
                        ),
                        html.Div(
                            className="lv-equilibrio-valores",
                            children=[
                                html.Div(
                                    className="lv-equilibrio-metrica",
                                    children=[
                                        html.Span(
                                            "x* · Presas",
                                            className="lv-equilibrio-etiqueta",
                                        ),
                                        html.Strong(
                                            f"{presas_eq:.1f}",
                                            className="lv-equilibrio-numero",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    className="lv-equilibrio-metrica",
                                    children=[
                                        html.Span(
                                            "y* · Depredadores",
                                            className="lv-equilibrio-etiqueta",
                                        ),
                                        html.Strong(
                                            f"{depredadores_eq:.1f}",
                                            className="lv-equilibrio-numero",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="lv-interpretacion",
                    children=[
                        html.P(
                            [
                                html.Strong("Evolución temporal. "),
                                "Muestra cómo varían las poblaciones de presas y depredadores.",
                            ]
                        ),
                        html.P(
                            [
                                html.Strong("Plano de fases. "),
                                "Muestra la trayectoria (x(t), y(t)) alrededor del equilibrio.",
                            ]
                        ),
                    ],
                ),
            ],
        )
        return figura_tiempo, figura_fases, lectura

    # Actualizar el valor visible junto al nombre de cada control.
    for _, control_id, _, _, _, _ in CONTROLES:
        app.clientside_callback(
            "function(valor) { return valor == null ? '—' : String(valor); }",
            Output(f"{control_id}-valor", "children"),
            Input(control_id, "value"),
        )

    @app.callback(
        Output("lv-modal-informacion", "is_open"),
        Output("lv-modal-titulo", "children"),
        Output("lv-modal-cuerpo", "children"),
        Input("lv-boton-modelo", "n_clicks"),
        Input("lv-boton-ecuaciones", "n_clicks"),
        Input("lv-boton-variables", "n_clicks"),
        Input("lv-cerrar-modal", "n_clicks"),
        State("lv-modal-titulo", "children"),
        State("lv-modal-cuerpo", "children"),
        prevent_initial_call=True,
    )
    def mostrar_informacion(
        n_modelo, n_ecuaciones, n_variables, n_cerrar, titulo, cuerpo
    ):
        accion = ctx.triggered_id
        if accion == "lv-cerrar-modal":
            return False, titulo, cuerpo
        secciones = {
            "lv-boton-modelo": "modelo",
            "lv-boton-ecuaciones": "ecuaciones",
            "lv-boton-variables": "variables",
        }
        if accion in secciones:
            nuevo_titulo, nuevo_cuerpo = contenido_modal(secciones[accion])
            return True, nuevo_titulo, nuevo_cuerpo
        return False, no_update, no_update

    # Callback del ciclo biologico (solo modal Ecosistema).
    registrar_callbacks_ecosistema(app)
