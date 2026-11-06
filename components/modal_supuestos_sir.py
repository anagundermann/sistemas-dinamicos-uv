"""Modal informativo para el laboratorio SIR.

Separa contenido educativo del cálculo, los gráficos y la presentación.
"""

from dash import Input, Output, State, ctx, html
import dash_bootstrap_components as dbc


ID_MODAL = "modal-supuestos-sir"
ID_ABRIR = "btn-abrir-modal-supuestos-sir"
ID_CERRAR = "btn-cerrar-modal-supuestos-sir"


def crear_boton_supuestos_sir():
    """Botón con el estilo unificado en tonos rosados y púrpuras."""
    return html.Button(
        "📋 Supuestos y datos",
        id=ID_ABRIR,
        n_clicks=0,
        className="sd-inicio",
        style={
            "fontSize": "0.85rem",
            "padding": "5px 10px",
            "cursor": "pointer",
            "borderColor": "#FBCFE8",
            "color": "#BE185D",
        },
    )


def crear_modal_supuestos_sir():
    """Modal estructurado en tarjetas de colores y cuadrícula estética."""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("📋 Supuestos del Modelo y Fuentes de Datos"),
                style={
                    "color": "#BE185D",
                    "fontWeight": "800",
                    "borderBottom": "1px solid #FCE7F3",
                },
            ),
            dbc.ModalBody(
                style={"backgroundColor": "#FDF2F8", "padding": "20px"},
                children=[
                    html.P(
                        "Este laboratorio permite explorar escenarios hipotéticos de propagación epidémica en las 16 regiones de Chile.",
                        style={"fontSize": "0.85rem", "color": "#475569", "marginBottom": "16px"}
                    ),
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "1fr 1fr",
                            "gap": "14px",
                        },
                        children=[
                            html.Div(
                                style={
                                    "backgroundColor": "white",
                                    "padding": "14px",
                                    "borderRadius": "12px",
                                    "border": "1px solid #FBCFE8",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.02)",
                                },
                                children=[
                                    html.H6(
                                        "📊 Población y Constantes",
                                        style={
                                            "color": "#DB2777",
                                            "fontWeight": "700",
                                            "fontSize": "0.85rem",
                                            "marginBottom": "6px",
                                        },
                                    ),
                                    html.P(
                                        "La población regional permanece constante (Sᵢ + Iᵢ + Rᵢ = Nᵢ). Las tasas β, γ y α se mantienen fijas durante cada simulación de 180 días (RK45).",
                                        style={
                                            "fontSize": "0.8rem",
                                            "color": "#475569",
                                            "margin": "0",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "backgroundColor": "white",
                                    "padding": "14px",
                                    "borderRadius": "12px",
                                    "border": "1px solid #FBCFE8",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.02)",
                                },
                                children=[
                                    html.H6(
                                        "🕸️ Red de Contactos",
                                        style={
                                            "color": "#DB2777",
                                            "fontWeight": "700",
                                            "fontSize": "0.85rem",
                                            "marginBottom": "6px",
                                        },
                                    ),
                                    html.P(
                                        "La epidemia inicia con 1.000 infectados en la región semilla. La red regional es ilustrativa para modelar el flujo de transmisión interregional.",
                                        style={
                                            "fontSize": "0.8rem",
                                            "color": "#475569",
                                            "margin": "0",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "backgroundColor": "white",
                                    "padding": "14px",
                                    "borderRadius": "12px",
                                    "border": "1px solid #FBCFE8",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.02)",
                                },
                                children=[
                                    html.H6(
                                        "🧪 Datos de Referencia",
                                        style={
                                            "color": "#DB2777",
                                            "fontWeight": "700",
                                            "fontSize": "0.85rem",
                                            "marginBottom": "6px",
                                        },
                                    ),
                                    html.P(
                                        "Las poblaciones Nᵢ provienen de datos históricos procesados en R desde el MINCiencia. Los casos acumulados son solo de referencia y no participan como infectados activos I(t).",
                                        style={
                                            "fontSize": "0.8rem",
                                            "color": "#475569",
                                            "margin": "0",
                                        },
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "backgroundColor": "white",
                                    "padding": "14px",
                                    "borderRadius": "12px",
                                    "border": "1px solid #FBCFE8",
                                    "boxShadow": "0 1px 3px rgba(0,0,0,0.02)",
                                },
                                children=[
                                    html.H6(
                                        "⚠️ Alcance Educativo",
                                        style={
                                            "color": "#DB2777",
                                            "fontWeight": "700",
                                            "fontSize": "0.85rem",
                                            "marginBottom": "6px",
                                        },
                                    ),
                                    html.P(
                                        "No se incluyen reinfecciones, demografía ni cuarentenas dinámicas. Diseñado estrictamente para comparar escenarios académicos y dinámicas en redes.",
                                        style={
                                            "fontSize": "0.8rem",
                                            "color": "#475569",
                                            "margin": "0",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            dbc.ModalFooter(
                style={"borderTop": "1px solid #FCE7F3"},
                children=[
                    dbc.Button(
                        "Cerrar",
                        id=ID_CERRAR,
                        n_clicks=0,
                        className="ms-auto",
                        style={
                            "backgroundColor": "#DB2777",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "8px",
                            "padding": "6px 16px",
                            "fontWeight": "600",
                        },
                    )
                ],
            ),
        ],
        id=ID_MODAL,
        is_open=False,
        centered=True,
        size="xl",
        scrollable=True,
    )


def registrar_callbacks_supuestos_sir(app):
    """Registra solo el abrir/cerrar del modal; no altera los cálculos SIR."""

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