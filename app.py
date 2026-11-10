"""Sistemas Dinamicos UV: aplicacion y navegacion principal."""

from urllib.parse import quote
import networkx as nx

from dash import Dash, Input, Output, ctx, dcc, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from pages import (
    introduccion,
    pendulo_simple,
    pendulo_doble,
    depredador_presa,
    sir,
)

from components.conceptos_biblioteca import (
    crear_consulta_conceptos,
    registrar_callbacks_conceptos,
)

from components.footer import crear_footer

# --------------------------------------------------
# PAGINAS Y LABORATORIOS
# --------------------------------------------------

PAGINAS = {
    "introduccion": ("Introducción", introduccion),
    "pendulo_simple": ("Péndulo simple", pendulo_simple),
    "pendulo_doble": ("Péndulo doble", pendulo_doble),
    "depredador_presa": ("Depredador-presa", depredador_presa),
    "sir": ("Modelo SIR", sir),
}

LABORATORIOS = [
    ("pendulo_simple", "Péndulo simple", "Oscilaciones", "azul"),
    ("pendulo_doble", "Péndulo doble", "Dinámica no lineal", "violeta"),
    ("depredador_presa", "Depredador-presa", "Lotka-Volterra", "turquesa"),
    ("sir", "Modelo SIR", "Epidemias", "sir"),
]


# --------------------------------------------------
# ILUSTRACIONES DE NAVEGACION
# --------------------------------------------------

TRAZOS = {
    "pendulo_simple": (
        '<path d="M7 46 Q26 67 59 42" '
        'fill="none" stroke="#B7CDFB" '
        'stroke-width="2.3" stroke-dasharray="0.5 5" '
        'stroke-linecap="round"/>'
        '<line x1="24" y1="8" x2="47" y2="49" '
        'stroke="#3B82F6" stroke-width="3.6" '
        'stroke-linecap="round"/>'
        '<circle cx="24" cy="8" r="3.2" fill="#243A57"/>'
        '<circle cx="47" cy="49" r="5.2" fill="#3B82F6"/>'
        '<circle cx="45" cy="47" r="1.3" fill="#A8CCFF"/>'
    ),
    "pendulo_doble": (
        '<path d="M18 51 C29 64 38 62 47 56 '
        'S68 40 71 49 C73 60 62 64 53 61" '
        'fill="none" stroke="#B9D0E6" '
        'stroke-width="2.2" stroke-dasharray="0.5 5" '
        'stroke-linecap="round"/>'
        '<line x1="20" y1="8" x2="39" y2="33" '
        'stroke="#3E6D99" stroke-width="3.6" '
        'stroke-linecap="round"/>'
        '<line x1="39" y1="33" x2="56" y2="53" '
        'stroke="#3E6D99" stroke-width="3.6" '
        'stroke-linecap="round"/>'
        '<circle cx="20" cy="8" r="3.1" fill="#243A57"/>'
        '<circle cx="39" cy="33" r="4.4" fill="#91B1CF"/>'
        '<circle cx="56" cy="53" r="5.2" fill="#3E6D99"/>'
        '<circle cx="54.5" cy="51.7" r="1.2" fill="#E8F2FA"/>'
    ),
    "depredador_presa": (
        '<path d="M4 41 C15 42 16 12 29 13 '
        'S44 48 57 35 S66 17 73 25" '
        'stroke="#14B8A6" fill="none" stroke-width="4"/>'
        '<path d="M4 54 C15 53 21 31 32 35 '
        'S48 58 60 48 S69 34 73 39" '
        'stroke="#EC4899" fill="none" stroke-width="4"/>'
    ),
    "sir": (
        '<path d="M4 13 Q23 13 35 44 T73 54" '
        'stroke="#694BC2" fill="none" stroke-width="3"/>'
        '<path d="M4 54 Q18 54 31 25 T73 54" '
        'stroke="#EC4899" fill="none" stroke-width="3"/>'
        '<path d="M4 57 Q35 55 47 34 T73 10" '
        'stroke="#784CD4" fill="none" stroke-width="3"/>'
    ),
}


def icono_modelo(clave):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 78 66">' + TRAZOS[clave] + "</svg>"
    )

    return "data:image/svg+xml;charset=utf-8," + quote(svg)


def crear_tarjeta_navegacion(clave, titulo, detalle, color):
    return html.Button(
        id=f"sd-nav-{clave}",
        n_clicks=0,
        className=f"sd-lab-card sd-lab-{color}",
        children=[
            html.Img(
                src=icono_modelo(clave),
                alt="",
                className="sd-lab-dibujo",
            ),
            html.Span(
                className="sd-lab-textos",
                children=[
                    html.Span(
                        titulo,
                        className="sd-lab-titulo",
                    ),
                    html.Span(
                        detalle,
                        className="sd-lab-detalle",
                    ),
                    html.Span(
                        "Explorar  →",
                        className="sd-lab-explorar",
                    ),
                ],
            ),
        ],
    )


# --------------------------------------------------
# APLICACION PRINCIPAL
# --------------------------------------------------

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

app.title = "Sistemas Dinámicos"


app.layout = html.Div(
    className="sd-app",
    children=[
        dcc.Store(
            id="sd-pagina-activa",
            data="introduccion",
        ),
        html.Header(
            className="sd-encabezado",
            children=[
                html.Div(
                    className="sd-marca",
                    children=[
                        html.H1(
                            "Sistemas Dinámicos",
                            className="sd-titulo-app",
                        ),
                    ],
                ),
                html.Div(
                    className="sd-acciones-cabecera",
                    children=[
                        crear_consulta_conceptos(),
                        html.Button(
                            "Inicio",
                            id="sd-ir-inicio",
                            n_clicks=0,
                            className="sd-inicio",
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            id="sd-layout",
            className="sd-layout",
            children=[
                html.Aside(
                    className="sd-laboratorios",
                    children=[
                        html.H2(
                            "Laboratorios",
                            className="sd-laboratorios-titulo",
                        ),
                        *[crear_tarjeta_navegacion(*modelo) for modelo in LABORATORIOS],
                    ],
                ),
                html.Main(
                    id="sd-contenido-pagina",
                    className="sd-contenido",
                ),
            ],
        ),
        # Footer compartido en todas las paginas.
        crear_footer(),
    ],
)


# --------------------------------------------------
# CAMBIO DE PAGINA
# --------------------------------------------------

DESTINOS = {f"sd-nav-{clave}": clave for clave, _, _, _ in LABORATORIOS}

DESTINOS["sd-ir-inicio"] = "introduccion"


@app.callback(
    Output("sd-pagina-activa", "data"),
    *[Input(identificador, "n_clicks") for identificador in DESTINOS],
    prevent_initial_call=True,
)
def cambiar_pagina(*_):
    destino = DESTINOS.get(ctx.triggered_id)

    if destino is None:
        raise PreventUpdate

    return destino


@app.callback(
    Output("sd-contenido-pagina", "children"),
    Output("sd-ir-inicio", "className"),
    Output("sd-layout", "className"),
    *[Output(f"sd-nav-{clave}", "className") for clave, _, _, _ in LABORATORIOS],
    Input("sd-pagina-activa", "data"),
)
def mostrar_pagina(pagina):

    nombre, modulo = PAGINAS.get(
        pagina,
        PAGINAS["introduccion"],
    )

    crear = getattr(modulo, "crear_pagina", None)

    if callable(crear):
        contenido = crear()
    else:
        contenido = html.Section(
            className="sd-tarjeta sd-vacia",
            children=[
                html.H2(nombre),
                html.P("Este laboratorio todavía está en preparación."),
            ],
        )

    # La portada muestra las tres columnas.
    # Los laboratorios ocupan todo el ancho disponible.

    if pagina == "introduccion":
        clase_layout = "sd-layout"
        clase_inicio = "sd-inicio activo"
    else:
        clase_layout = "sd-layout sd-layout-laboratorio"
        clase_inicio = "sd-inicio"

    clases_labs = [
        f"sd-lab-card sd-lab-{color}" + (" activo" if pagina == clave else "")
        for clave, _, _, color in LABORATORIOS
    ]

    return (
        contenido,
        clase_inicio,
        clase_layout,
        *clases_labs,
    )


# --------------------------------------------------
# CALLBACKS
# --------------------------------------------------

for _, modulo in PAGINAS.values():
    registrar = getattr(
        modulo,
        "registrar_callbacks",
        None,
    )

    if callable(registrar):
        registrar(app)

registrar_callbacks_conceptos(app)


# --------------------------------------------------
# EJECUCION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=False,
        host="127.0.0.1",
        port=8082,
    )
