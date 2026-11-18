"""Ciclo ecologico interactivo sin Cytoscape.

Cuatro botones nativos de Dash, conectores fijos con CSS Grid y
una sola etapa seleccionada. No altera el modelo matematico.

Mantiene la interfaz esperada por pages/depredador_presa.py:
    crear_contenido_ecosistema()
    registrar_callbacks_ecosistema(app)

Estilos adicionales: assets/zzz-ecosistema-botones.css
"""

from urllib.parse import quote

from dash import Input, Output, State, ctx, html


COLOR_CONEJOS = "#2e7d5b"
COLOR_ZORROS = "#7c3aed"

ETAPAS = {
    "paso-1": (
        "1 · Aumentan los conejos",
        "Con pocos zorros, disminuye la depredación y las presas crecen.",
    ),
    "paso-2": (
        "2 · Aumentan los zorros",
        "La abundancia de conejos favorece el aumento de depredadores.",
    ),
    "paso-3": (
        "3 · Disminuyen los conejos",
        "Más zorros intensifican la depredación y las presas disminuyen.",
    ),
    "paso-4": (
        "4 · Disminuyen los zorros",
        "Al escasear los conejos, disminuyen los zorros y las presas se recuperan.",
    ),
}

# (id del conector, etapa de origen, direccion, etiqueta)
ARISTAS = [
    ("mas-alimento", "paso-1", "derecha", "más alimento"),
    ("mas-depredacion", "paso-2", "abajo", "más depredación"),
    ("menos-alimento", "paso-3", "izquierda", "menos alimento"),
    ("menos-presion", "paso-4", "arriba", "menos presión"),
]


# ------------------------------------------------------------
# COMPONENTES VISUALES
# ------------------------------------------------------------


def _boton_etapa(paso, etiqueta, poblacion):
    return html.Button(
        etiqueta,
        id=f"lv-eco-boton-{paso}",
        n_clicks=0,
        type="button",
        className=f"lv-eco-nodo lv-eco-nodo-{poblacion} lv-eco-nodo-{paso}",
        title="Seleccionar etapa del ciclo",
    )


def _clase_conector(direccion, origen, activo=False):
    """Color de identidad de la flecha que sale de cada etapa."""
    poblacion = "conejo" if origen in ("paso-1", "paso-3") else "zorro"
    clase = f"lv-eco-conector lv-eco-conector-{direccion} lv-eco-conector-{poblacion}"
    return clase + (" lv-eco-conector-activo" if activo else "")


def _conector(arista_id, origen, direccion, etiqueta):
    """Flecha larga: el trazo y la punta se dibujan con CSS nativo."""
    return html.Div(
        [
            html.Span(etiqueta, className="lv-eco-conector-texto"),
            html.Span(
                "",
                className="lv-eco-conector-linea",
                **{"aria-hidden": "true"},
            ),
        ],
        id=f"lv-eco-conector-{arista_id}",
        className=_clase_conector(direccion, origen),
    )


def crear_detalle_ciclo(paso_activo=None):
    """Texto de invitacion o explicacion de la etapa seleccionada."""
    if paso_activo not in ETAPAS:
        mano = (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 24 24" fill="none" '
            'stroke="#454545" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M22 14a8 8 0 0 1-8 8"/>'
            '<path d="M18 11v-1a2 2 0 0 0-2-2a2 2 0 0 0-2 2"/>'
            '<path d="M14 10V9a2 2 0 0 0-2-2a2 2 0 0 0-2 2v1"/>'
            '<path d="M10 9.5V4a2 2 0 0 0-2-2a2 2 0 0 0-2 2v10"/>'
            '<path d="M18 11a2 2 0 1 1 4 0v3a8 8 0 0 1-8 8h-2'
            "c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 "
            '2.83-2.82L7 15"/>'
            "</svg>"
        )
        return html.Div(
            className="lv-eco-detalle-contenido lv-eco-invitacion",
            children=[
                html.Span(
                    html.Img(
                        src="data:image/svg+xml," + quote(mano, safe=""),
                        alt="",
                        style={"width": "27px", "height": "27px", "display": "block"},
                    ),
                    className="lv-eco-invitacion-icono",
                    **{"aria-hidden": "true"},
                ),
                html.Div(
                    [
                        html.Strong(
                            "Explora las etapas del ciclo",
                            className="lv-eco-invitacion-titulo",
                        ),
                        html.P(
                            "Selecciona uno de los cuatro recuadros para "
                            "conocer cómo cambian las poblaciones.",
                            className="lv-eco-invitacion-texto",
                        ),
                    ],
                    className="lv-eco-invitacion-mensaje",
                ),
            ],
        )

    titulo, descripcion = ETAPAS[paso_activo]
    return html.Div(
        className="lv-eco-detalle-contenido",
        children=[
            html.Strong(titulo, className="lv-eco-detalle-titulo"),
            html.P(descripcion),
            html.P(
                "Haz clic otra vez en la etapa seleccionada para volver al inicio.",
                className="lv-eco-pista-reinicio",
            ),
        ],
    )


def crear_ciclo_ecosistema():
    """Ciclo de cuatro etapas, sin grafo ni coordenadas fijas."""
    return html.Section(
        className="lv-eco-panel-ciclo",
        children=[
            html.H3("El ciclo depredador–presa"),
            html.Div(
                className="lv-eco-ciclo-grid",
                children=[
                    _boton_etapa("paso-1", "↑ Conejos", "conejo"),
                    _conector(*ARISTAS[0]),
                    _boton_etapa("paso-2", "↑ Zorros", "zorro"),
                    _conector(*ARISTAS[3]),
                    html.Button(
                        "CICLO ECOLÓGICO",
                        id="lv-eco-reiniciar",
                        n_clicks=0,
                        disabled=True,
                        type="button",
                        className="lv-eco-ciclo-centro",
                        title="Volver a la invitación inicial",
                    ),
                    _conector(*ARISTAS[1]),
                    _boton_etapa("paso-4", "↓ Zorros", "zorro"),
                    _conector(*ARISTAS[2]),
                    _boton_etapa("paso-3", "↓ Conejos", "conejo"),
                ],
            ),
        ],
    )


def crear_contenido_ecosistema(modelo_seleccionado="clasico"):
    """Mantiene el mismo ciclo y adapta los supuestos al modelo activo."""
    if modelo_seleccionado == "logistico":
        texto_simplificacion = (
            "Los recursos disponibles limitan el crecimiento natural de los "
            "conejos mediante la capacidad de carga K. Se supone que los zorros "
            "solo se alimentan de conejos. No considera migraciones, "
            "enfermedades ni estaciones."
        )
    else:
        texto_simplificacion = (
            "Supone alimento ilimitado para las presas y que los zorros solo "
            "se alimentan de ellas. No considera migraciones, enfermedades "
            "ni estaciones."
        )

    return html.Div(
        className="lv-eco",
        children=[
            html.Div(id="lv-eco-etapa-elegida", children="", style={"display": "none"}),
            html.Div(
                className="lv-eco-columnas",
                children=[
                    crear_ciclo_ecosistema(),
                    html.Div(
                        className="lv-eco-contexto",
                        children=[
                            html.Section(
                                className="lv-eco-seccion",
                                children=[
                                    html.H3("Una relación depredador–presa"),
                                    html.P(
                                        "Conejos (presas) y zorros (depredadores) "
                                        "se influyen mutuamente."
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-eco-detalle",
                                children=[
                                    html.P(
                                        "",
                                        id="lv-eco-etiqueta",
                                        className="lv-eco-detalle-etiqueta",
                                    ),
                                    html.Div(
                                        id="lv-eco-detalle",
                                        children=crear_detalle_ciclo(),
                                        **{"aria-live": "polite"},
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-eco-idea",
                                children=[
                                    html.H3("Idea clave"),
                                    html.P(
                                        "Durante las oscilaciones, los zorros alcanzan "
                                        "su máximo después de los conejos."
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-eco-seccion",
                                children=[
                                    html.H3("¿Qué simplifica el modelo?"),
                                    html.P(texto_simplificacion),
                                ],
                            ),
                            html.P(
                                "Es un modelo teórico, no una predicción exacta.",
                                className="lv-eco-nota",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def registrar_callbacks_ecosistema(app):
    """Seleccion persistente; repetir clic o pulsar centro restablece el inicio."""

    @app.callback(
        Output("lv-eco-etapa-elegida", "children"),
        Output("lv-eco-detalle", "children"),
        Output("lv-eco-etiqueta", "children"),
        Output("lv-eco-reiniciar", "children"),
        Output("lv-eco-reiniciar", "disabled"),
        Output("lv-eco-reiniciar", "className"),
        *[Output(f"lv-eco-boton-{paso}", "className") for paso in ETAPAS],
        *[
            Output(f"lv-eco-conector-{id_arista}", "className")
            for id_arista, _, _, _ in ARISTAS
        ],
        *[Input(f"lv-eco-boton-{paso}", "n_clicks") for paso in ETAPAS],
        Input("lv-eco-reiniciar", "n_clicks"),
        State("lv-eco-etapa-elegida", "children"),
        prevent_initial_call=True,
    )
    def actualizar_etapa_ecosistema(*argumentos):
        anterior = argumentos[-1]
        disparador = ctx.triggered_id

        # El mismo nodo se deselecciona con un segundo clic.
        # El boton del centro tambien limpia la seleccion directamente.
        if disparador == "lv-eco-reiniciar":
            elegido = None
        elif isinstance(disparador, str) and disparador.startswith("lv-eco-boton-"):
            paso = disparador.removeprefix("lv-eco-boton-")
            elegido = None if paso == anterior else paso
        else:
            elegido = None

        if elegido not in ETAPAS:
            elegido = None

        clases_botones = [
            (
                f"lv-eco-nodo lv-eco-nodo-{'conejo' if paso_id in ('paso-1', 'paso-3') else 'zorro'} "
                f"lv-eco-nodo-{paso_id}"
                + (" lv-eco-nodo-elegido" if paso_id == elegido else "")
            )
            for paso_id in ETAPAS
        ]
        clases_aristas = [
            _clase_conector(direccion, origen, activo=(origen == elegido))
            for _, origen, direccion, _ in ARISTAS
        ]
        return (
            elegido or "",
            crear_detalle_ciclo(elegido),
            "ETAPA SELECCIONADA" if elegido else "",
            "↺ Volver al inicio" if elegido else "CICLO ECOLÓGICO",
            not bool(elegido),
            "lv-eco-ciclo-centro lv-eco-ciclo-reinicio-disponible"
            if elegido
            else "lv-eco-ciclo-centro",
            *clases_botones,
            *clases_aristas,
        )
