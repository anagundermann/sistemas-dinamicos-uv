"""Pagina de introduccion de Sistemas Dinamicos UV."""

from urllib.parse import quote

from dash import dcc, html


# --------------------------------------------------
# ILUSTRACIONES
# --------------------------------------------------


ORBIPLOT = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="40 20 380 285">

  <!-- Circunferencia de referencia -->
  <circle cx="230" cy="170" r="102"
    fill="none" stroke="#DDD4FE" stroke-width="2"
    stroke-dasharray="7 8"/>

  <!-- Trayectoria violeta original -->
  <g transform="rotate(-26 230 170)">
    <ellipse cx="230" cy="170" rx="169" ry="70"
      fill="none" stroke="#8C79D4" stroke-width="3"/>

    <!-- Punto violeta -->
    <circle cx="399" cy="170" r="9"
      fill="#7C3AED" stroke="#FFFFFF" stroke-width="2"/>

    <!-- Punto rosado sobre la misma trayectoria -->
    <circle cx="61" cy="170" r="9"
      fill="#EC4899" stroke="#FFFFFF" stroke-width="2"/>
  </g>

  <!-- Trayectoria turquesa original -->
  <g transform="rotate(26 230 170)">
    <ellipse cx="230" cy="170" rx="164" ry="68"
      fill="none" stroke="#14B8A6" stroke-width="3"/>

    <!-- Punto turquesa -->
    <circle cx="230" cy="238" r="9"
      fill="#14B8A6" stroke="#FFFFFF" stroke-width="2"/>
  </g>

  <!-- Centro fijo de referencia -->
  <circle cx="230" cy="170" r="34" fill="#F3EFFF"/>
  <circle cx="230" cy="170" r="16" fill="#7C3AED"/>

</svg>
"""

GRAFICO_TIEMPO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 125">
  <path d="M24 10 V105 H345" fill="none"
    stroke="#B9B1D3" stroke-width="2"/>
  <path d="M24 35 H345 M24 70 H345"
    stroke="#EBE7F6" stroke-dasharray="4 6"/>
  <path d="M25 60 C50 15 75 18 100 60
    S150 105 175 60 S225 15 250 60
    S300 105 345 55"
    fill="none" stroke="#7C3AED"
    stroke-width="4" stroke-linecap="round"/>
  <path d="M25 86 C58 96 78 32 112 40
    S161 105 194 88 S245 27 277 40
    S319 98 345 89"
    fill="none" stroke="#14B8A6"
    stroke-width="4" stroke-linecap="round"/>
  <text x="11" y="17" font-size="12" fill="#62617D">x</text>
  <text x="342" y="121" font-size="12" fill="#62617D">t</text>
</svg>
"""

GRAFICO_PARAMETROS = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 110">
  <rect x="16" y="15" width="325" height="80" rx="15"
    fill="#FAF9FF" stroke="#E4DDFC"/>
  <path d="M46 40 H311 M46 72 H311"
    stroke="#D6C9F5" stroke-width="5"
    stroke-linecap="round"/>
  <path d="M46 40 H193" stroke="#7C3AED"
    stroke-width="5" stroke-linecap="round"/>
  <path d="M46 72 H252" stroke="#14B8A6"
    stroke-width="5" stroke-linecap="round"/>
  <circle cx="193" cy="40" r="12" fill="#7C3AED"/>
  <circle cx="252" cy="72" r="12" fill="#14B8A6"/>
</svg>
"""


def imagen_svg(svg):
    return "data:image/svg+xml;charset=utf-8," + quote(svg.strip())


# --------------------------------------------------
# PAGINA PRINCIPAL
# --------------------------------------------------


def crear_pagina():
    """Portada compacta: dos tarjetas centrales y dos tarjetas a la derecha."""
    return html.Div(
        className="sd-intro",
        children=[
            # Columna central: la portada y las preguntas son tarjetas separadas.
            html.Div(
                className="sd-intro-central",
                children=[
                    html.Section(
                        className="sd-tarjeta sd-portada-central",
                        children=[
                            html.Div(
                                "MATEMÁTICA EN MOVIMIENTO",
                                className="sd-sobretitulo",
                            ),
                            html.H2(
                                "Explora cómo evolucionan los sistemas",
                                className="sd-portada-titulo",
                            ),
                            html.P(
                                "Visualiza trayectorias, modifica parámetros y compara sistemas.",
                                className="sd-portada-descripcion",
                            ),
                            html.Img(
                                src=imagen_svg(ORBIPLOT),
                                alt="Ilustración de trayectorias dinámicas",
                                className="sd-portada-ilustracion",
                            ),
                        ],
                    ),
                    html.Section(
                        className="sd-tarjeta sd-portada-preguntas",
                        children=[
                            html.H3(
                                "¿Qué podemos investigar?",
                                className="sd-info-titulo",
                            ),
                            html.Div(
                                className="sd-portada-preguntas-grid",
                                children=[
                                    html.Div(
                                        className="sd-portada-pregunta",
                                        children=[
                                            html.Span("1"),
                                            html.P(
                                                "Los conceptos matemáticos de cada modelo."
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="sd-portada-pregunta",
                                        children=[
                                            html.Span("2"),
                                            html.P(
                                                "El efecto de cambiar los parámetros."
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="sd-portada-pregunta",
                                        children=[
                                            html.Span("3"),
                                            html.P(
                                                "La influencia de las condiciones iniciales."
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="sd-portada-pregunta",
                                        children=[
                                            html.Span("4"),
                                            html.P(
                                                "Los patrones que presentan las trayectorias."
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Columna derecha: información matemática e instrucciones.
            html.Aside(
                className="sd-intro-derecha",
                children=[
                    html.Section(
                        className="sd-tarjeta sd-info-card sd-info-matematica",
                        children=[
                            html.H3(
                                "¿Qué tienen en común?",
                                className="sd-info-titulo",
                            ),
                            html.Div(
                                dcc.Markdown(
                                    r"$$\dot{\mathbf{x}}(t)"
                                    r"=F(\mathbf{x}(t);\mathbf{p})$$",
                                    mathjax=True,
                                ),
                                className="sd-formula",
                            ),
                            html.P(
                                "Todos describen cómo evoluciona el estado de un "
                                "sistema a partir de una ley matemática."
                            ),
                            html.Img(
                                src=imagen_svg(GRAFICO_TIEMPO),
                                alt="Curvas de evolución temporal",
                                className="sd-info-ilustracion",
                            ),
                        ],
                    ),
                    html.Section(
                        className="sd-tarjeta sd-info-card sd-info-instrucciones",
                        children=[
                            html.H3(
                                "¿Cómo utilizar el laboratorio?",
                                className="sd-info-titulo",
                            ),
                            html.Ol(
                                className="sd-pasos",
                                children=[
                                    html.Li("Elige un modelo."),
                                    html.Li(
                                        "Ajusta sus parámetros y condiciones iniciales."
                                    ),
                                    html.Li("Observa y compara los resultados."),
                                ],
                            ),
                            html.Img(
                                src=imagen_svg(GRAFICO_PARAMETROS),
                                alt="Controles de parámetros",
                                className="sd-info-ilustracion",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
