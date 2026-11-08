"""Biblioteca matematica: un solo modal con navegacion lateral.

Los textos y formulas se mantienen en components/biblioteca_datos.py.
Esta interfaz solo selecciona y presenta las fichas existentes.
"""

from dash import ALL, Input, Output, ctx, dcc, html, remount
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from components.conceptos_biblioteca_datos import CONCEPTOS


CLAVES_CONCEPTOS = tuple(CONCEPTOS)
CLAVE_INICIAL = CLAVES_CONCEPTOS[0]
DATO_INICIAL = CONCEPTOS[CLAVE_INICIAL]


def crear_consulta_conceptos():
    """Crea el acceso global y la biblioteca de conceptos matematicos."""
    return html.Div(
        className="sd-conceptos-control",
        children=[
            # Un solo clic abre la biblioteca; ya no hay menu desplegable previo.
            html.Button(
                "Biblioteca matemática",
                id="sd-abrir-conceptos",
                n_clicks=0,
                type="button",
                className="sd-inicio sd-consultar-boton",
                **{"aria-haspopup": "dialog", "aria-controls": "sd-concepto-modal"},
            ),
            dbc.Modal(
                id="sd-concepto-modal",
                is_open=False,
                centered=True,
                scrollable=False,
                size="xl",
                class_name="sd-concepto-modal",
                children=[
                    dbc.ModalHeader(
                        close_button=False,
                        class_name="sd-modal-cabecera",
                        children=[
                            html.Div(
                                className="sd-modal-encabezado-textos",
                                children=[
                                    html.Span(
                                        "BIBLIOTECA MATEMÁTICA",
                                        className="sd-modal-etiqueta",
                                    ),
                                    dbc.ModalTitle(
                                        id="sd-concepto-titulo",
                                        class_name="sd-modal-titulo",
                                        children=CONCEPTOS[CLAVE_INICIAL]["titulo"],
                                    ),
                                ],
                            ),
                            html.Button(
                                id="sd-cerrar-concepto-x",
                                n_clicks=0,
                                type="button",
                                title="Cerrar ventana",
                                className="btn-close sd-modal-cerrar-x",
                                **{"aria-label": "Cerrar ventana"},
                            ),
                        ],
                    ),
                    dbc.ModalBody(
                        class_name="sd-modal-cuerpo",
                        children=[
                            # Columna izquierda: los diez nombres, sin submodales.
                            html.Nav(
                                className="sd-modal-lateral",
                                **{"aria-label": "Conceptos matemáticos"},
                                children=[
                                    html.Button(
                                        dato["titulo"],
                                        id={
                                            "type": "sd-opcion-concepto",
                                            "index": clave,
                                        },
                                        n_clicks=0,
                                        type="button",
                                        className=(
                                            "sd-concepto-opcion "
                                            "sd-concepto-opcion-activa"
                                            if clave == CLAVE_INICIAL
                                            else "sd-concepto-opcion"
                                        ),
                                    )
                                    for clave, dato in CONCEPTOS.items()
                                ],
                            ),
                            # Columna derecha: misma ficha, con distribucion renovada.
                            html.Div(
                                className="sd-modal-principal",
                                children=[
                                    html.Div(
                                        className="sd-modal-ficha",
                                        children=[
                                            html.Div(
                                                className="sd-modal-grid-superior",
                                                children=[
                                                    html.Section(
                                                        className=(
                                                            "sd-concepto-seccion "
                                                            "sd-concepto-seccion-matematica"
                                                        ),
                                                        children=[
                                                            html.H4(
                                                                "Definición matemática",
                                                                className="sd-modal-seccion-titulo",
                                                            ),
                                                            html.P(
                                                                id="sd-concepto-descripcion",
                                                                children=DATO_INICIAL[
                                                                    "definicion_texto"
                                                                ],
                                                                className="sd-modal-texto",
                                                            ),
                                                            html.Div(
                                                                id="sd-concepto-formula-contenedor",
                                                                className="sd-modal-formula",
                                                                children=dcc.Markdown(
                                                                    id="sd-concepto-formula",
                                                                    children="$$\n"
                                                                    + DATO_INICIAL[
                                                                        "formula"
                                                                    ]
                                                                    + "\n$$",
                                                                    mathjax=True,
                                                                    className="sd-modal-mathjax",
                                                                ),
                                                            ),
                                                        ],
                                                    ),
                                                    html.Section(
                                                        className=(
                                                            "sd-concepto-seccion "
                                                            "sd-concepto-seccion-notacion"
                                                        ),
                                                        children=[
                                                            html.H4(
                                                                "Donde",
                                                                className="sd-modal-seccion-titulo",
                                                            ),
                                                            html.Div(
                                                                id="sd-concepto-notacion-contenedor",
                                                                children=dcc.Markdown(
                                                                    id="sd-concepto-notacion",
                                                                    children=DATO_INICIAL.get(
                                                                        "notacion", ""
                                                                    ),
                                                                    mathjax=True,
                                                                    className="sd-modal-notacion",
                                                                ),
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            html.Section(
                                                className=(
                                                    "sd-concepto-seccion "
                                                    "sd-concepto-seccion-intuitiva"
                                                ),
                                                children=[
                                                    html.H4(
                                                        "Interpretación intuitiva",
                                                        className="sd-modal-seccion-titulo",
                                                    ),
                                                    html.P(
                                                        id="sd-concepto-explicacion",
                                                        children=DATO_INICIAL[
                                                            "explicacion"
                                                        ],
                                                        className="sd-modal-texto",
                                                    ),
                                                ],
                                            ),
                                            html.Section(
                                                className=(
                                                    "sd-concepto-seccion "
                                                    "sd-concepto-seccion-propiedades"
                                                ),
                                                children=[
                                                    html.H4(
                                                        "Propiedades matemáticas",
                                                        className="sd-modal-seccion-titulo",
                                                    ),
                                                    html.P(
                                                        id="sd-concepto-propiedades",
                                                        children=DATO_INICIAL[
                                                            "propiedades"
                                                        ],
                                                        className="sd-modal-texto",
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
            ),
        ],
    )


def registrar_callbacks_conceptos(app):
    """Registra acciones separadas para cierre y seleccion de conceptos.

    El estado abierto/cerrado no depende de las salidas dinamicas del menu.
    Asi, cerrar el modal no intenta modificar elementos dentro de el.
    """

    @app.callback(
        Output("sd-concepto-modal", "is_open"),
        Input("sd-abrir-conceptos", "n_clicks"),
        Input("sd-cerrar-concepto-x", "n_clicks"),
        prevent_initial_call=True,
    )
    def cambiar_visibilidad_conceptos(_abrir, _cerrar_x):
        origen = ctx.triggered_id

        if origen == "sd-abrir-conceptos":
            return True

        if origen == "sd-cerrar-concepto-x":
            return False

        raise PreventUpdate

    @app.callback(
        Output("sd-concepto-titulo", "children"),
        Output("sd-concepto-descripcion", "children"),
        Output("sd-concepto-formula-contenedor", "children"),
        Output("sd-concepto-notacion-contenedor", "children"),
        Output("sd-concepto-explicacion", "children"),
        Output("sd-concepto-propiedades", "children"),
        Output({"type": "sd-opcion-concepto", "index": ALL}, "className"),
        Input({"type": "sd-opcion-concepto", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def seleccionar_concepto(_clics_conceptos):
        origen = ctx.triggered_id

        if not isinstance(origen, dict):
            raise PreventUpdate
        if origen.get("type") != "sd-opcion-concepto":
            raise PreventUpdate

        clave = origen.get("index")
        if clave not in CONCEPTOS:
            raise PreventUpdate

        dato = CONCEPTOS[clave]
        clases = [
            "sd-concepto-opcion sd-concepto-opcion-activa"
            if item == clave
            else "sd-concepto-opcion"
            for item in CLAVES_CONCEPTOS
        ]

        return (
            dato["titulo"],
            dato["definicion_texto"],
            # Remontar cada Markdown para que MathJax regenere sus simbolos.
            remount(
                dcc.Markdown(
                    id="sd-concepto-formula",
                    children="$$\n" + dato["formula"] + "\n$$",
                    mathjax=True,
                    className="sd-modal-mathjax",
                )
            ),
            remount(
                dcc.Markdown(
                    id="sd-concepto-notacion",
                    children=dato.get("notacion", ""),
                    mathjax=True,
                    className="sd-modal-notacion",
                )
            ),
            dato["explicacion"],
            dato["propiedades"],
            clases,
        )
