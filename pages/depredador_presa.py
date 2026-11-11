"""Laboratorio interactivo de depredador-presa (Lotka-Volterra).

La presentacion de esta pagina se controla en assets/zz-depredador-presa.css.

Se conservan los seis parametros originales y la animacion compartida.
El selector alterna entre el modelo clasico y el de crecimiento logistico.

"""

from components.analisis_cuantitativo_lv import (
    crear_boton_analisis_lv,
    crear_modal_analisis_lv,
    registrar_callbacks_analisis_lv,
)

from components.barra_animacion_lv import (
    crear_barra_animacion_vista_previa,
    preparar_datos_animacion,
    crear_formas_guia,
    crear_anotaciones_guia,
    _estado_visible,
)

from dash import Input, Output, Patch, State, ctx, dcc, get_asset_url, html, no_update

import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import numpy as np
from scipy.signal import find_peaks

from components.ecosistema_lv import (
    crear_contenido_ecosistema,
    registrar_callbacks_ecosistema,
)

from components.modelo_matematico_lv import crear_contenido_modelo_matematico

from components.equilibrios_estabilidad_lv import crear_contenido_analisis_sistema

from components.trayectorias_oscilaciones_lv import crear_contenido_ciclos_periodo

from models.modelo_lotka_volterra import (
    calcular_equilibrio,
    simular_lotka_volterra,
)
from models.modelo_lotka_logistico import (
    calcular_equilibrio_logistico,
    simular_lotka_logistico,
)


COLOR_PRESAS = "#14B8A6"

COLOR_DEPREDADORES = "#7C3AED"


# Configuracion separada para editar los controles sin tocar el layout.


CONTROLES = [
    ("α · Crecimiento de presas", "lv-alpha", 0.1, 1.2, 0.05, 0.65),
    ("β · Intensidad de depredación", "lv-beta", 0.005, 0.05, 0.001, 0.018),
    ("γ · Mortalidad de depredadores", "lv-gamma", 0.1, 1.0, 0.05, 0.55),
    ("δ · Reproducción por depredación", "lv-delta", 0.005, 0.04, 0.001, 0.012),
    ("Presas iniciales", "lv-presas-0", 2, 120, 1, 60),
    ("Depredadores iniciales", "lv-depredadores-0", 2, 100, 1, 20),
]

# Control adicional del segundo modelo: siempre reserva su altura.
CONTROL_K = ("K · Capacidad de carga", "lv-k", 50, 300, 10, 120)


# Los indices de las trazas de tiempo son fijos para respetar
# barra_animacion_lv.py: 0=presas, 1=depredadores,
# 2/3=cursor de animacion, 4/5=extremos locales.


def _traza_cursor_vacia(nombre, color):
    """Reserva el indice del cursor sin dibujar puntos antes de Play."""
    return go.Scatter(
        x=[],
        y=[],
        mode="markers",
        name=nombre,
        showlegend=False,
        hoverinfo="skip",
        marker={
            "size": 10,
            "color": color,
            "line": {"color": "#FFFFFF", "width": 1.8},
        },
    )


def _traza_extremos(tiempos, valores, nombre, color, guia_activa):
    """Maximos y minimos locales interiores de toda la solucion.

    Se ignoran ondulaciones insignificantes debidas a redondeo numerico.
    Los extremos en t=0 y t=T no se clasifican como locales.
    """
    tiempos = np.asarray(tiempos, dtype=float)
    valores = np.asarray(valores, dtype=float)
    prominencia = max(0.001 * float(np.ptp(valores)), 1e-7)
    indices_max, _ = find_peaks(valores, prominence=prominencia)
    indices_min, _ = find_peaks(-valores, prominence=prominencia)

    # Un trace por poblacion permite marcar ambos tipos sin agregar
    # entradas en la leyenda ni cambiar el codigo de la animacion.
    indices = sorted([int(i) for i in indices_max] + [int(i) for i in indices_min])
    maximos = set(int(i) for i in indices_max)
    etiquetas = ["Máx" if i in maximos else "Mín" for i in indices]

    return go.Scatter(
        x=tiempos[indices],
        y=valores[indices],
        customdata=etiquetas,
        mode="markers",
        name=f"Extremos · {nombre}",
        visible=bool(guia_activa),
        showlegend=False,
        marker={
            "size": 8,
            "color": color,
            "line": {"color": "#FFFFFF", "width": 1.5},
        },
        hovertemplate="%{customdata} · t=%{x:.1f} · %{y:.1f}<extra></extra>",
        hoverlabel={
            "bgcolor": "#F3F6FA",
            "bordercolor": "#CBD5E1",
            "font": {"family": "Arial, sans-serif", "size": 11, "color": "#334155"},
        },
    )


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
                figure={
                    "data": [],
                    "layout": {
                        "xaxis": {"visible": False},
                        "yaxis": {"visible": False},
                        "paper_bgcolor": "white",
                        "plot_bgcolor": "white",
                    },
                },
                config={
                    "displayModeBar": False,
                    "scrollZoom": False,
                    "responsive": True,
                },
            ),
        ],
    )


def crear_panel_estado():
    """Lectura compacta de la solucion, dentro del panel de controles."""

    return html.Div(
        className="lv-estado-actual",
        children=[
            html.Div(
                className="lv-estado-encabezado",
                children=[
                    html.Span(
                        "Estado de las poblaciones",
                        className="lv-estado-titulo",
                    ),
                    html.Div(
                        className="lv-estado-herramientas",
                        children=[
                            dbc.Switch(
                                id="lv-guia-vertical",
                                label="Guía",
                                value=False,
                                class_name="lv-guia-interruptor",
                            ),
                            html.Span(
                                "t = 0.0",
                                id="lv-estado-tiempo",
                                className="lv-estado-tiempo",
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="lv-estado-valores",
                children=[
                    html.Div(
                        className="lv-estado-celda lv-estado-celda-presas",
                        children=[
                            html.Span("Presas · x(t)", className="lv-estado-etiqueta"),
                            html.Strong(
                                "60.0",
                                id="lv-estado-presas",
                                className="lv-estado-numero",
                            ),
                        ],
                    ),
                    html.Div(
                        className="lv-estado-celda lv-estado-celda-depredadores",
                        children=[
                            html.Span(
                                "Depredadores · y(t)",
                                className="lv-estado-etiqueta",
                            ),
                            html.Strong(
                                "20.0",
                                id="lv-estado-depredadores",
                                className="lv-estado-numero",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def crear_pagina():

    return html.Div(
        className="lv-pagina",
        children=[
            # Modelo activo: se usa en la simulacion y en el selector.
            dcc.Store(id="lv-modelo-seleccionado", data="clasico"),
            html.Header(
                className="lv-cabecera",
                children=[
                    html.H2(
                        "Depredador–Presa · Lotka–Volterra",
                        id="lv-titulo-modelo",
                        className="sd-titulo-seccion lv-titulo lv-titulo-clasico",
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
                                "Equilibrios y estabilidad",
                                id="lv-boton-variables",
                                className="lv-boton-info",
                                n_clicks=0,
                            ),
                            dbc.Button(
                                "Trayectorias y oscilaciones",
                                id="lv-boton-ciclos",
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
                                "Parámetros del modelo",
                                className="sd-titulo-tarjeta",
                            ),
                            html.Div(
                                className="lv-lista-controles",
                                children=[crear_control(*datos) for datos in CONTROLES],
                            ),
                            html.Div(
                                id="lv-control-k-contenedor",
                                className="lv-control-extra",
                                style={"visibility": "hidden", "opacity": 0},
                                children=crear_control(*CONTROL_K),
                            ),
                            crear_panel_estado(),
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
                            # Selector compartido: la animacion usa la solucion activa.
                            html.Div(
                                className="lv-selector-modelo",
                                children=[
                                    html.Div(
                                        className="lv-selector-modelo-fila",
                                        children=[
                                            html.Div(
                                                className="lv-modelo-siluetas",
                                                children=[
                                                    html.Img(
                                                        src=get_asset_url(
                                                            "zorro-lineal.svg"
                                                        ),
                                                        alt="",
                                                        className="lv-modelo-zorro",
                                                    ),
                                                    html.Img(
                                                        src=get_asset_url(
                                                            "conejo-lineal.svg"
                                                        ),
                                                        alt="",
                                                        className="lv-modelo-conejo",
                                                    ),
                                                    crear_boton_analisis_lv(),
                                                ],
                                            ),
                                            html.Div(
                                                className="lv-selector-modelo-botones",
                                                children=[
                                                    html.Span(
                                                        "Modelo:",
                                                        className="lv-selector-modelo-etiqueta",
                                                    ),
                                                    html.Button(
                                                        "Lotka–Volterra clásico",
                                                        id="lv-boton-clasico",
                                                        className="lv-modelo-boton lv-modelo-boton-activo",
                                                        n_clicks=0,
                                                        type="button",
                                                    ),
                                                    html.Button(
                                                        "Crecimiento logístico",
                                                        id="lv-boton-logistico",
                                                        className="lv-modelo-boton",
                                                        n_clicks=0,
                                                        type="button",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.Span(
                                        "",
                                        id="lv-modelo-aviso",
                                        className="lv-modelo-aviso",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            crear_modal_analisis_lv(),
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
            html.Div(
                "Integración numérica: RK45 (Dormand–Prince), paso adaptativo · SciPy (solve_ivp)",
                style={
                    "textAlign": "center",
                    "fontSize": "11px",
                    "color": "#64748B",
                    "marginTop": "12px",
                    "paddingBottom": "8px",
                },
            ),
        ],
    )


def contenido_modal(seccion, modelo_seleccionado, alpha, beta, gamma, delta, k):
    """Contenido educativo correspondiente al modelo activo."""

    if seccion == "modelo":
        return "Ecosistema · Zorros y conejos", crear_contenido_ecosistema()

    if seccion == "ecuaciones":
        titulo = (
            "Modelo matemático · Lotka–Volterra logístico"
            if modelo_seleccionado == "logistico"
            else "Modelo matemático · Lotka–Volterra"
        )
        return titulo, crear_contenido_modelo_matematico(modelo_seleccionado)

    if seccion == "ciclos":
        titulo = (
            "Trayectorias y oscilaciones · Lotka–Volterra logístico"
            if modelo_seleccionado == "logistico"
            else "Trayectorias y oscilaciones · Lotka–Volterra"
        )

        return titulo, crear_contenido_ciclos_periodo(
            modelo_seleccionado, alpha, beta, gamma, delta, k
        )

    titulo = (
        "Equilibrios y estabilidad · Lotka–Volterra logístico"
        if modelo_seleccionado == "logistico"
        else "Equilibrios y estabilidad · Lotka–Volterra"
    )

    return titulo, crear_contenido_analisis_sistema(
        modelo_seleccionado, alpha, beta, gamma, delta, k
    )


def registrar_callbacks(app):

    @app.callback(
        Output("lv-grafico-tiempo", "figure"),
        Output("lv-grafico-fases", "figure"),
        Output("lv-lectura", "children"),
        Output("lv-estado-tiempo", "children"),
        Output("lv-estado-presas", "children"),
        Output("lv-estado-depredadores", "children"),
        Output("lv-animacion-datos", "data"),
        Input("lv-alpha", "value"),
        Input("lv-beta", "value"),
        Input("lv-gamma", "value"),
        Input("lv-delta", "value"),
        Input("lv-presas-0", "value"),
        Input("lv-depredadores-0", "value"),
        Input("lv-k", "value"),
        Input("lv-modelo-seleccionado", "data"),
        State("lv-guia-vertical", "value"),
    )
    def actualizar_laboratorio(
        alpha,
        beta,
        gamma,
        delta,
        presas_0,
        depredadores_0,
        k,
        modelo_seleccionado,
        guia_activa,
    ):
        """Resuelve solo el modelo seleccionado; reutiliza ambos graficos."""
        modelo_logistico = modelo_seleccionado == "logistico"

        if modelo_logistico:
            tiempos, presas, depredadores = simular_lotka_logistico(
                alpha, beta, gamma, delta, presas_0, depredadores_0, k
            )
            equilibrio_positivo = calcular_equilibrio_logistico(
                alpha, beta, gamma, delta, k
            )

            if equilibrio_positivo is not None:
                presas_eq, depredadores_eq = equilibrio_positivo
                titulo_equilibrio = "Equilibrio de coexistencia"
                texto_fases = (
                    "La trayectoria puede aproximarse al equilibrio de "
                    "coexistencia, con o sin oscilaciones amortiguadas."
                )
            else:
                # Cuando K <= gamma/delta no hay coexistencia positiva.
                presas_eq, depredadores_eq = float(k), 0.0
                titulo_equilibrio = "Equilibrio sin depredadores"
                texto_fases = (
                    "No existe equilibrio positivo de coexistencia para "
                    "este K. Los depredadores tienden a extinguirse y las "
                    "presas tienden a K."
                )
        else:
            tiempos, presas, depredadores = simular_lotka_volterra(
                alpha, beta, gamma, delta, presas_0, depredadores_0
            )
            presas_eq, depredadores_eq = calcular_equilibrio(alpha, beta, gamma, delta)
            titulo_equilibrio = "Equilibrio de coexistencia"
            texto_fases = (
                "Muestra la trayectoria (x(t), y(t)) alrededor del equilibrio."
            )

        # Una unica solucion alimenta los graficos, el mouse y la animacion.
        datos = preparar_datos_animacion(tiempos, presas, depredadores)

        figura_tiempo = go.Figure()

        figura_tiempo.add_trace(
            go.Scatter(
                x=tiempos,
                y=presas,
                mode="lines",
                name="Presas",
                hoverinfo="none",  # Conserva hoverData sin mostrar recuadro flotante.
                line={"color": COLOR_PRESAS, "width": 3},
            )
        )

        figura_tiempo.add_trace(
            go.Scatter(
                x=tiempos,
                y=depredadores,
                mode="lines",
                name="Depredadores",
                hoverinfo="none",
                line={"color": COLOR_DEPREDADORES, "width": 3},
            )
        )

        # Reservar los indices 2 y 3 para los marcadores que mueve Play.
        # Los indices 4 y 5 son los extremos fijos (visibles solo con Guia).
        figura_tiempo.add_trace(_traza_cursor_vacia("Cursor · Presas", COLOR_PRESAS))
        figura_tiempo.add_trace(
            _traza_cursor_vacia("Cursor · Depredadores", COLOR_DEPREDADORES)
        )
        figura_tiempo.add_trace(
            _traza_extremos(tiempos, presas, "Presas", COLOR_PRESAS, guia_activa)
        )
        figura_tiempo.add_trace(
            _traza_extremos(
                tiempos,
                depredadores,
                "Depredadores",
                COLOR_DEPREDADORES,
                guia_activa,
            )
        )

        figura_tiempo.update_layout(
            # Espacio real para titulos y numeros de los dos ejes.
            margin={"l": 70, "r": 18, "t": 35, "b": 78},
            xaxis={
                "title": {"text": "Tiempo", "standoff": 14},
                "automargin": True,
                "range": datos["rango_t"],
                "autorange": False,
                "fixedrange": True,
                "zeroline": False,
                # Guia dibujada como shape: sirve tanto con mouse como con Play.
                "showspikes": False,
            },
            yaxis={
                "title": {"text": "Población (unidades del modelo)", "standoff": 12},
                "automargin": True,
                "range": datos["rango_poblacion"],
                "autorange": False,
                "fixedrange": True,
                "zeroline": False,
            },
            hovermode="x" if guia_activa else "closest",
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
                "labelalias": {"0": ""},
                "range": datos["rango_x_fases"],
                "autorange": False,
                "fixedrange": True,
                "zeroline": False,
            },
            yaxis={
                "title": {"text": "Depredadores (y)", "standoff": 12},
                "automargin": True,
                "labelalias": {"0": ""},
                "range": datos["rango_y_fases"],
                "autorange": False,
                "fixedrange": True,
                "zeroline": False,
            },
            dragmode=False,
            legend={"orientation": "h", "y": 1.12, "x": 0},
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        # Las dos guias usan la solucion ya calculada y nunca reescalan ejes.

        formas_t, formas_f = crear_formas_guia(
            tiempos[0], presas[0], depredadores[0], datos, guia_activa
        )

        figura_tiempo.update_layout(shapes=formas_t)

        figura_fases.update_layout(shapes=formas_f)

        figura_fases.update_layout(
            annotations=crear_anotaciones_guia(
                presas[0], depredadores[0], datos, guia_activa
            )
        )

        lectura = html.Div(
            className="lv-resumen",
            children=[
                html.Div(
                    className="lv-equilibrio-recuadro",
                    children=[
                        html.Div(
                            titulo_equilibrio,
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
                                texto_fases,
                            ]
                        ),
                    ],
                ),
            ],
        )

        return (
            figura_tiempo,
            figura_fases,
            lectura,
            f"t = {float(tiempos[0]):.1f}",
            f"{float(presas[0]):.1f}",
            f"{float(depredadores[0]):.1f}",
            datos,
        )

    @app.callback(
        Output("lv-grafico-tiempo", "figure", allow_duplicate=True),
        Output("lv-grafico-fases", "figure", allow_duplicate=True),
        Input("lv-guia-vertical", "value"),
        State("lv-grafico-tiempo", "figure"),
        State("lv-grafico-fases", "figure"),
        State("lv-animacion-datos", "data"),
        prevent_initial_call=True,
    )
    def alternar_guia_vertical(guia_activa, figura_tiempo, figura_fases, datos):
        """Muestra guias sincronizadas, sin variar escalas ni recalcular ODE."""

        temporal = Patch()

        fases = Patch()

        temporal["layout"]["hovermode"] = "x" if guia_activa else "closest"

        temporal["layout"]["xaxis"]["showspikes"] = False

        # Los indices 4 y 5 contienen extremos de presas y depredadores.
        # Se muestran/ocultan sin alterar las curvas ni recalcular la solucion.
        if figura_tiempo and len(figura_tiempo.get("data", [])) >= 6:
            temporal["data"][4]["visible"] = bool(guia_activa)
            temporal["data"][5]["visible"] = bool(guia_activa)

        # No se muestran ejes fijos del origen: usamos proyecciones dinamicas.

        estado = _estado_visible(figura_tiempo, datos)

        if estado is not None:
            formas_t, formas_f = crear_formas_guia(*estado, datos, guia_activa)

        else:
            formas_t, formas_f = [], []

        temporal["layout"]["shapes"] = formas_t

        fases["layout"]["shapes"] = formas_f

        if estado is not None:
            fases["layout"]["annotations"] = crear_anotaciones_guia(
                estado[1], estado[2], datos, guia_activa
            )

        else:
            fases["layout"]["annotations"] = []

        return temporal, fases

    # Actualizar el valor visible junto al nombre de cada control.

    for _, control_id, _, _, _, _ in [*CONTROLES, CONTROL_K]:
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
        Input("lv-boton-ciclos", "n_clicks"),
        Input("lv-cerrar-modal", "n_clicks"),
        State("lv-modal-titulo", "children"),
        State("lv-modal-cuerpo", "children"),
        State("lv-modelo-seleccionado", "data"),
        State("lv-alpha", "value"),
        State("lv-beta", "value"),
        State("lv-gamma", "value"),
        State("lv-delta", "value"),
        State("lv-k", "value"),
        prevent_initial_call=True,
    )
    def mostrar_informacion(
        n_modelo,
        n_ecuaciones,
        n_variables,
        n_ciclos,
        n_cerrar,
        titulo,
        cuerpo,
        modelo_seleccionado,
        alpha,
        beta,
        gamma,
        delta,
        k,
    ):

        accion = ctx.triggered_id

        if accion == "lv-cerrar-modal":
            return False, titulo, cuerpo

        secciones = {
            "lv-boton-modelo": "modelo",
            "lv-boton-ecuaciones": "ecuaciones",
            "lv-boton-variables": "variables",
            "lv-boton-ciclos": "ciclos",
        }

        if accion in secciones:
            nuevo_titulo, nuevo_cuerpo = contenido_modal(
                secciones[accion],
                modelo_seleccionado,
                alpha,
                beta,
                gamma,
                delta,
                k,
            )

            return True, nuevo_titulo, nuevo_cuerpo

        return False, no_update, no_update

    @app.callback(
        Output("lv-modelo-seleccionado", "data"),
        Output("lv-control-k-contenedor", "style"),
        Output("lv-boton-clasico", "className"),
        Output("lv-boton-logistico", "className"),
        Output("lv-modelo-aviso", "children"),
        Output("lv-titulo-modelo", "children"),
        Output("lv-titulo-modelo", "className"),
        Input("lv-boton-clasico", "n_clicks"),
        Input("lv-boton-logistico", "n_clicks"),
        prevent_initial_call=True,
    )
    def seleccionar_modelo(n_clasico, n_logistico):
        """Alterna entre ambos sistemas conservando alturas y colores."""
        if ctx.triggered_id == "lv-boton-logistico":
            return (
                "logistico",
                {"visibility": "visible", "opacity": 1},
                "lv-modelo-boton",
                "lv-modelo-boton lv-modelo-boton-activo",
                "",
                "Depredador–Presa · Lotka–Volterra logístico",
                "sd-titulo-seccion lv-titulo lv-titulo-logistico",
            )

        return (
            "clasico",
            {"visibility": "hidden", "opacity": 0},
            "lv-modelo-boton lv-modelo-boton-activo",
            "lv-modelo-boton",
            "",
            "Depredador–Presa · Lotka–Volterra",
            "sd-titulo-seccion lv-titulo lv-titulo-clasico",
        )

    # Callback del ciclo biologico (solo modal Ecosistema).

    registrar_callbacks_ecosistema(app)
    registrar_callbacks_analisis_lv(app)
