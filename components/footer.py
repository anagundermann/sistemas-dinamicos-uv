"""Footer compartido de Sistemas Dinamicos UV."""

from dash import html


def crear_footer():
    return html.Footer(
        className="sd-footer",
        children=[
            # COLUMNA IZQUIERDA
            html.Div(
                className="sd-footer-bloque",
                children=[
                    html.Strong(
                        "Sistemas Dinámicos UV",
                        className="sd-footer-titulo",
                    ),
                    html.Span(
                        "Laboratorio matemático interactivo",
                        className="sd-footer-texto",
                    ),
                ],
            ),
            # COLUMNA CENTRAL
            html.Div(
                className="sd-footer-bloque sd-footer-integrantes",
                children=[
                    html.Strong(
                        "Desarrollado por",
                        className="sd-footer-subtitulo",
                    ),
                    html.Span(
                        "Macarena Valdebenito · Fabián Zanetta · Ana Gundermann",
                        className="sd-footer-texto sd-footer-nombres",
                    ),
                ],
            ),
            # COLUMNA DERECHA
            html.Div(
                className="sd-footer-bloque sd-footer-final",
                children=[
                    html.Strong(
                        "Universidad de Valparaíso",
                        className="sd-footer-subtitulo",
                    ),
                    html.Span(
                        "Visualización de Datos · 2026",
                        className="sd-footer-texto",
                    ),
                ],
            ),
        ],
    )
