"""Menu y ventana de conceptos matematicos."""

from dash import ALL, Input, Output, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

from conceptos_data import CONCEPTOS


def crear_consulta_conceptos():
    return html.Div(
        className="sd-conceptos-control",
        children=[
            # MENU SIN BUSCADOR
            dbc.DropdownMenu(
                label="Consultar conceptos",
                color="light",
                direction="down",
                caret=True,
                class_name="sd-conceptos-menu",
                toggle_class_name="sd-inicio",
                children=[
                    dbc.DropdownMenuItem(
                        dato["titulo"],
                        id={
                            "type": "sd-opcion-concepto",
                            "index": clave,
                        },
                        n_clicks=0,
                    )
                    for clave, dato in CONCEPTOS.items()
                ],
            ),
            # VENTANA MATEMATICA
            dbc.Modal(
                id="sd-concepto-modal",
                is_open=False,
                centered=True,
                scrollable=True,
                size="lg",
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
                                    ),
                                ],
                            ),
                            html.Button(
                                "×",
                                id="sd-cerrar-concepto-x",
                                n_clicks=0,
                                type="button",
                                title="Cerrar ventana",
                                className="sd-modal-cerrar-x",
                                **{"aria-label": "Cerrar ventana"},
                            ),
                        ],
                    ),
                    # CUERPO: OPCION E
                    dbc.ModalBody(
                        class_name="sd-modal-cuerpo",
                        children=[
                            # FILA SUPERIOR:
                            # DEFINICION MATEMATICA + NOTACION
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
                                                className="sd-modal-texto",
                                            ),
                                            html.Div(
                                                className="sd-modal-formula",
                                                children=[
                                                    dcc.Markdown(
                                                        id="sd-concepto-formula",
                                                        mathjax=True,
                                                        className="sd-modal-mathjax",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    # EXPLICACION DE LOS SIMBOLOS
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
                                            dcc.Markdown(
                                                id="sd-concepto-notacion",
                                                mathjax=True,
                                                className="sd-modal-notacion",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            # INTERPRETACION: ANCHO COMPLETO
                            html.Section(
                                className=(
                                    "sd-concepto-seccion sd-concepto-seccion-intuitiva"
                                ),
                                children=[
                                    html.H4(
                                        "Interpretación intuitiva",
                                        className="sd-modal-seccion-titulo",
                                    ),
                                    html.P(
                                        id="sd-concepto-explicacion",
                                        className="sd-modal-texto",
                                    ),
                                ],
                            ),
                            # PROPIEDADES: ANCHO COMPLETO
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
                                        className="sd-modal-texto",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dbc.ModalFooter(
                        class_name="sd-modal-pie",
                        children=[
                            html.Button(
                                "Cerrar",
                                id="sd-cerrar-concepto",
                                n_clicks=0,
                                type="button",
                                className="sd-modal-boton",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def registrar_callbacks_conceptos(app):

    @app.callback(
        Output("sd-concepto-modal", "is_open"),
        Output("sd-concepto-titulo", "children"),
        Output("sd-concepto-descripcion", "children"),
        Output("sd-concepto-formula", "children"),
        Output("sd-concepto-notacion", "children"),
        Output("sd-concepto-explicacion", "children"),
        Output("sd-concepto-propiedades", "children"),
        Input(
            {"type": "sd-opcion-concepto", "index": ALL},
            "n_clicks",
        ),
        Input("sd-cerrar-concepto", "n_clicks"),
        Input("sd-cerrar-concepto-x", "n_clicks"),
        prevent_initial_call=True,
    )
    def actualizar_ventana_concepto(
        _clics_conceptos,
        _clic_cerrar,
        _clic_cerrar_x,
    ):
        origen = ctx.triggered_id

        if origen in (
            "sd-cerrar-concepto",
            "sd-cerrar-concepto-x",
        ):
            return (
                False,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        if not isinstance(origen, dict):
            raise PreventUpdate

        if origen.get("type") != "sd-opcion-concepto":
            raise PreventUpdate

        clave = origen.get("index")

        if clave not in CONCEPTOS:
            raise PreventUpdate

        dato = CONCEPTOS[clave]

        formula = "$$\n" + dato["formula"] + "\n$$"

        return (
            True,
            dato["titulo"],
            dato["definicion_texto"],
            formula,
            dato.get("notacion", ""),
            dato["explicacion"],
            dato["propiedades"],
        )
