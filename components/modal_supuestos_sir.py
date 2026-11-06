"""Modal informativo para el laboratorio SIR.

Separa contenido educativo del calculo, los graficos y la presentacion.
"""

from dash import Input, Output, State, ctx, html
import dash_bootstrap_components as dbc


ID_MODAL = "modal-supuestos-sir"
ID_ABRIR = "btn-abrir-modal-supuestos-sir"
ID_CERRAR = "btn-cerrar-modal-supuestos-sir"


def crear_boton_supuestos_sir():
    """Boton con el mismo aspecto de los dos modales existentes."""
    return html.Button(
        "📋 Supuestos y datos",
        id=ID_ABRIR,
        n_clicks=0,
        className="sd-inicio",
        style={
            "fontSize": "0.85rem",
            "padding": "5px 10px",
            "cursor": "pointer",
        },
    )


def crear_modal_supuestos_sir():
    """Supuestos que el visitante necesita para interpretar la simulacion."""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Supuestos y datos"),
                style={"color": "#1E1B4B", "fontWeight": "800"},
            ),
            dbc.ModalBody(
                [
                    html.P(
                        "Este laboratorio permite explorar escenarios hipoteticos "
                        "de propagacion epidemica en las 16 regiones de Chile."
                    ),
                    html.H5(
                        "Supuestos de la simulación", className="sd-titulo-tarjeta"
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "La población de cada región permanece constante: "
                                "Sᵢ + Iᵢ + Rᵢ = Nᵢ."
                            ),
                            html.Li(
                                "La epidemia comienza con 1.000 infectados en la "
                                "región seleccionada; inicialmente no hay recuperados "
                                "ni infectados en las otras regiones."
                            ),
                            html.Li(
                                "Las tasas de infección local (β), recuperación (γ) "
                                "y transmisión entre regiones (α) son constantes "
                                "durante cada simulación."
                            ),
                            html.Li(
                                "La red de regiones es ilustrativa. Sus conexiones "
                                "no proceden de mediciones reales de movilidad."
                            ),
                            html.Li(
                                "El modelo no incluye reinfecciones, nacimientos, "
                                "muertes demográficas ni cambios de comportamiento."
                            ),
                            html.Li(
                                "Se simulan 180 días mediante una aproximación "
                                "numérica con RK45."
                            ),
                        ]
                    ),
                    html.H5("Datos de referencia", className="sd-titulo-tarjeta"),
                    html.P(
                        "Las poblaciones regionales provienen de registros "
                        "históricos de Chile, procesados y agrupados por región "
                        "en R a partir del conjunto Datos-COVID19 del Ministerio "
                        "de Ciencia. Estas poblaciones se utilizan como Nᵢ."
                    ),
                    html.H5(
                        "Cómo interpretar los resultados", className="sd-titulo-tarjeta"
                    ),
                    html.Ul(
                        [
                            html.Li(
                                "Las curvas S, I y R, el grafo y el mapa de calor "
                                "son resultados simulados; no representan casos "
                                "observados de COVID-19."
                            ),
                            html.Li(
                                "El CSV contiene también casos confirmados "
                                "acumulados, pero no se usan como infectados "
                                "activos del modelo."
                            ),
                            html.Li(
                                "β/γ y el umbral mostrado son referencias del SIR "
                                "homogéneo sin red, no indicadores completos de "
                                "la propagación interregional."
                            ),
                            html.Li(
                                "Los resultados sirven para comparar escenarios "
                                "educativos, no para predecir o reconstruir "
                                "la epidemia histórica en Chile."
                            ),
                        ]
                    ),
                ]
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Cerrar",
                    id=ID_CERRAR,
                    n_clicks=0,
                    className="ms-auto",
                    style={
                        "backgroundColor": "#7C3AED",
                        "color": "white",
                        "border": "none",
                    },
                )
            ),
        ],
        id=ID_MODAL,
        is_open=False,
        centered=True,
        size="lg",
        scrollable=True,
    )


def registrar_callbacks_supuestos_sir(app):
    """Registra solo el abrir/cerrar del modal; no altera los calculos SIR."""

    @app.callback(
        Output(ID_MODAL, "is_open"),
        Input(ID_ABRIR, "n_clicks"),
        Input(ID_CERRAR, "n_clicks"),
        State(ID_MODAL, "is_open"),
    )
    def alternar_modal_supuestos_sir(n_abrir, n_cerrar, abierto):
        if ctx.triggered_id == ID_ABRIR:
            return True
        if ctx.triggered_id == ID_CERRAR:
            return False
        return abierto
