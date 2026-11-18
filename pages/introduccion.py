"""Portada de Sistemas Dinamicos Continuos.

La portada presenta las tres areas de aplicacion; la navegacion real
por laboratorios permanece en app.py, sin enlaces duplicados.
"""

from urllib.parse import quote

from dash import html


# Iconos vectoriales de la portada. Todos se generan localmente, sin internet.
ICONOS = {
    "fisica": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
          <g fill="none" stroke="#1D5696" stroke-width="2.8"
             stroke-linecap="round">
            <ellipse cx="40" cy="40" rx="27" ry="11"/>
            <ellipse cx="40" cy="40" rx="27" ry="11"
                     transform="rotate(60 40 40)"/>
            <ellipse cx="40" cy="40" rx="27" ry="11"
                     transform="rotate(120 40 40)"/>
          </g>
          <circle cx="40" cy="40" r="7.5" fill="#287FE2"/>
          <circle cx="64" cy="30" r="3" fill="#3B91E8"/>
        </svg>
    """,
    "ecologia": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
          <path d="M15 64 C16 34 33 23 64 16 C62 47 45 63 24 60"
                fill="none" stroke="#078970" stroke-width="4"
                stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M16 66 C26 53 38 42 54 31"
                fill="none" stroke="#078970" stroke-width="4"
                stroke-linecap="round"/>
        </svg>
    """,
    "salud": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
          <g fill="#7B43C7">
            <circle cx="40" cy="24" r="9"/>
            <path d="M24 55 V47 C24 37 31 34 40 34 S56 37 56 47 V55
                     Q56 60 51 60 H29 Q24 60 24 55Z"/>
          </g>
          <g fill="#9969DC">
            <circle cx="19" cy="31" r="7"/>
            <path d="M7 57 V49 C7 41 12 39 19 39 C22 39 23 39 25 40
                     C22 45 22 52 22 61 H12 Q7 61 7 57Z"/>
            <circle cx="61" cy="31" r="7"/>
            <path d="M73 57 V49 C73 41 68 39 61 39 C58 39 57 39 55 40
                     C58 45 58 52 58 61 H68 Q73 61 73 57Z"/>
          </g>
        </svg>
    """,
}


# Ondas suaves, meramente decorativas, de la esquina superior y el borde inferior.
ONDA_SUPERIOR = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 270"
     preserveAspectRatio="none">
  <defs>
    <linearGradient id="onda1" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#E9F3FF" stop-opacity="0"/>
      <stop offset="1" stop-color="#A8D0FA" stop-opacity="0.67"/>
    </linearGradient>
    <linearGradient id="onda2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#E4F1FE" stop-opacity="0"/>
      <stop offset="1" stop-color="#78B6F2" stop-opacity="0.38"/>
    </linearGradient>
  </defs>
  <path d="M0 170 C135 176 183 63 297 95 C408 127 468 -7 620 29
           L620 270 L0 270 Z" fill="url(#onda1)"/>
  <path d="M0 195 C120 157 214 210 321 117 C441 17 510 221 620 94
           L620 270 L0 270 Z" fill="url(#onda2)"/>
  <path d="M0 223 C168 218 202 126 313 163 C443 207 478 90 620 139"
        fill="none" stroke="#93C6FA" stroke-opacity="0.42" stroke-width="2"/>
</svg>
"""

ONDA_INFERIOR = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 90"
     preserveAspectRatio="none">
  <path d="M0 63 C154 5 257 110 405 56 C561 5 659 96 799 50
           C945 9 1000 17 1100 34 L1100 90 L0 90 Z"
        fill="#E9F4FF" fill-opacity="0.80"/>
  <path d="M0 80 C194 37 323 89 493 70 C672 47 729 85 887 47
           C976 24 1056 47 1100 62 L1100 90 L0 90 Z"
        fill="#C9E4FC" fill-opacity="0.36"/>
</svg>
"""


AREAS = (
    {
        "clave": "fisica",
        "titulo": "Física",
        "enfoque": "EXPERIMENTACIÓN NUMÉRICA",
        "descripcion": (
            "Explora el movimiento de péndulos simples y dobles, "
            "analiza sus trayectorias y la influencia de los parámetros."
        ),
    },
    {
        "clave": "ecologia",
        "titulo": "Ecología",
        "enfoque": "EXPLORACIÓN EDUCATIVA",
        "descripcion": (
            "Estudia Lotka–Volterra con curvas, plano de fases y análisis "
            "cuantitativo y cualitativo de sus equilibrios."
        ),
    },
    {
        "clave": "salud",
        "titulo": "Salud pública",
        "enfoque": "MODELACIÓN APLICADA",
        "descripcion": (
            "Analiza escenarios epidemiológicos con el modelo SIR, "
            "compara resultados e interpreta indicadores en una red de regiones."
        ),
    },
)


def imagen_svg(svg):
    """Convierte el SVG local en una imagen para Dash."""
    return "data:image/svg+xml;charset=utf-8," + quote(svg.strip())


def crear_area(area):
    """Cada seccion presenta una experiencia; no es un boton."""
    return html.Section(
        className=f"sd-editorial-fila sd-editorial-fila-{area['clave']}",
        children=[
            html.Div(
                className="sd-editorial-circulo",
                children=html.Img(
                    src=imagen_svg(ICONOS[area["clave"]]),
                    alt="",
                    className="sd-editorial-icono",
                    **{"aria-hidden": "true"},
                ),
            ),
            html.Div(className="sd-editorial-acento", **{"aria-hidden": "true"}),
            html.Div(
                className="sd-editorial-identidad",
                children=[
                    html.H3(area["titulo"], className="sd-editorial-area-titulo"),
                    html.Span(area["enfoque"], className="sd-editorial-area-enfoque"),
                ],
            ),
            html.P(area["descripcion"], className="sd-editorial-area-texto"),
        ],
    )


def crear_pagina():
    """Portada con presentacion a la izquierda y botones reales a la derecha."""
    return html.Div(
        className="sd-intro sd-intro-editorial",
        children=[
            html.Img(
                src=imagen_svg(ONDA_SUPERIOR),
                alt="",
                className="sd-editorial-onda-superior",
                **{"aria-hidden": "true"},
            ),
            html.Img(
                src=imagen_svg(ONDA_INFERIOR),
                alt="",
                className="sd-editorial-onda-inferior",
                **{"aria-hidden": "true"},
            ),
            html.Div(
                className="sd-editorial-contenido",
                children=[
                    html.Div(
                        className="sd-editorial-encabezado",
                        children=[
                            html.Span(
                                "LABORATORIO MATEMÁTICO INTERACTIVO",
                                className="sd-editorial-etiqueta",
                            ),
                            html.H2(
                                children=[
                                    html.Span("La", className="sd-editorial-la"),
                                    " matemática en movimiento",
                                ],
                                className="sd-editorial-titulo",
                            ),
                            html.P(
                                "Explora, experimenta y analiza modelos de sistemas "
                                "dinámicos que describen fenómenos de la física, "
                                "la ecología y la salud pública.",
                                className="sd-editorial-descripcion",
                            ),
                        ],
                    ),
                    html.Div(
                        className="sd-editorial-areas",
                        children=[crear_area(area) for area in AREAS],
                    ),
                ],
            ),
        ],
    )
