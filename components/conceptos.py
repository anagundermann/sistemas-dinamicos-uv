"""Selector de conceptos y ventana modal de definiciones."""

from dash import Input, Output, ctx, dcc, html
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

from conceptos_data import CONCEPTOS


# --------------------------------------------------
# COMPONENTE DE CONSULTA
# --------------------------------------------------


def crear_consulta_conceptos():

    return html.Section(
        className="sd-tarjeta sd-info-card sd-conceptos",
        children=[
            html.H3(
                "Consultar conceptos",
                className="sd-info-titulo",
            ),
            dcc.Dropdown(
                id="sd-selector-concepto",
                options=[
                    {
                        "label": dato["titulo"],
                        "value": clave,
                    }
                    for clave, dato in CONCEPTOS.items()
                ],
                placeholder="Selecciona un concepto",
                value=None,
                clearable=True,
                className="sd-concepto-selector",
            ),
            html.P(
                "Selecciona un término para ver su definición "
                "matemática y una explicación sencilla.",
                className="sd-conceptos-ayuda",
            ),
            dbc.Modal(
                id="sd-concepto-modal",
                is_open=False,
                centered=True,
                size="lg",
                children=[
                    dbc.ModalHeader(
                        dbc.ModalTitle(
                            id="sd-concepto-titulo",
                        ),
                    ),
                    dbc.ModalBody(
                        [
                            html.H4(
                                "Definición matemática",
                                className="sd-modal-subtitulo",
                            ),
                            dcc.Markdown(
                                id="sd-concepto-formula",
                                mathjax=True,
                            ),
                            html.H4(
                                "En palabras simples",
                                className="sd-modal-subtitulo",
                            ),
                            html.P(
                                id="sd-concepto-explicacion",
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Cerrar",
                            id="sd-cerrar-concepto",
                            color="secondary",
                        )
                    ),
                ],
            ),
        ],
    )


# --------------------------------------------------
# CALLBACK DE LA VENTANA MODAL
# --------------------------------------------------


def registrar_callbacks_conceptos(app):

    @app.callback(
        Output("sd-concepto-modal", "is_open"),
        Output("sd-concepto-titulo", "children"),
        Output("sd-concepto-formula", "children"),
        Output("sd-concepto-explicacion", "children"),
        Input("sd-selector-concepto", "value"),
        Input("sd-cerrar-concepto", "n_clicks"),
        prevent_initial_call=True,
    )
    def mostrar_concepto(clave, _):

        if ctx.triggered_id == "sd-cerrar-concepto":
            return False, "", "", ""

        if clave not in CONCEPTOS:
            raise PreventUpdate

        dato = CONCEPTOS[clave]

        return (
            True,
            dato["titulo"],
            dato["definicion"],
            dato["explicacion"],
        )
