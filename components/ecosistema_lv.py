"""Modal Ecosistema: ciclo interactivo de zorros y conejos.

Toda la logica del diagrama es Python y Dash Cytoscape. Los estilos
externos de la ventana se encuentran en assets/zz-ecosistema-lv.css.
El modal (cabecera y pie) se reutiliza desde pages/depredador_presa.py.
"""

from dash import Input, Output, html
import dash_cytoscape as cyto


# Datos editables; identificadores tecnicos ASCII.
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

# Cuatro posiciones constantes: un diagrama explicativo, no un editor.
# Las dimensiones del elemento Cytoscape son responsivas mediante CSS.
NODOS = [
    ("paso-1", "↑ Conejos", "conejo", 110, 85),
    ("paso-2", "↑ Zorros", "zorro", 395, 85),
    ("paso-3", "↓ Conejos", "conejo", 395, 275),
    ("paso-4", "↓ Zorros", "zorro", 110, 275),
]

ARISTAS = [
    ("arista-1", "paso-1", "paso-2", "más alimento"),
    ("arista-2", "paso-2", "paso-3", "más depredación"),
    ("arista-3", "paso-3", "paso-4", "menos alimento"),
    ("arista-4", "paso-4", "paso-1", "menos presión"),
]

ESTILO_BASE = [
    {
        "selector": "node",
        "style": {
            "shape": "round-rectangle",
            "width": 130,
            "height": 62,
            "background-color": "#ffffff",
            "border-width": 3,
            "label": "data(label)",
            "color": "#29254d",
            "font-family": "Segoe UI, Arial, sans-serif",
            "font-size": 17,
            "font-weight": 700,
            "text-halign": "center",
            "text-valign": "center",
            "text-wrap": "none",
            "overlay-opacity": 0,
        },
    },
    {"selector": 'node[tipo = "conejo"]', "style": {"border-color": "#2e7d5b"}},
    {"selector": 'node[tipo = "zorro"]', "style": {"border-color": "#d9822b"}},
    {
        "selector": "edge",
        "style": {
            "curve-style": "straight",
            "line-color": "#b8c2be",
            "width": 3,
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#b8c2be",
            "arrow-scale": 1,
            "label": "data(label)",
            "color": "#57645f",
            "font-family": "Segoe UI, Arial, sans-serif",
            "font-size": 11,
            "text-background-color": "#ffffff",
            "text-background-opacity": 1,
            "text-background-padding": 4,
            "text-rotation": "none",
            "overlay-opacity": 0,
        },
    },
    {
        "selector": "node.activo",
        "style": {
            "background-color": "#C0267D",
            "border-color": "#C0267D",
            "color": "#FFFFFF",
            "underlay-color": "#EC4899",
            "underlay-opacity": 0.30,
            "underlay-padding": 9,
        },
    },
    {
        "selector": "edge.activo",
        "style": {
            "line-color": "#C0267D",
            "width": 5,
            "target-arrow-color": "#C0267D",
            # Sin cambiar arrow-scale: evita una punta desproporcionada.
        },
    },
]


def crear_elementos_ciclo(paso_activo="paso-1"):
    """Devuelve nodos y aristas; activa el nodo y su arista saliente."""
    elementos = []
    for nodo_id, etiqueta, tipo, x, y in NODOS:
        elementos.append(
            {
                "data": {"id": nodo_id, "label": etiqueta, "tipo": tipo},
                "position": {"x": x, "y": y},
                "classes": "activo" if nodo_id == paso_activo else "",
            }
        )
    for arista_id, origen, destino, etiqueta in ARISTAS:
        elementos.append(
            {
                "data": {
                    "id": arista_id,
                    "source": origen,
                    "target": destino,
                    "label": etiqueta,
                },
                "classes": "activo" if origen == paso_activo else "",
            }
        )
    return elementos


def crear_detalle_ciclo(paso_activo="paso-1"):
    titulo, descripcion = ETAPAS.get(paso_activo, ETAPAS["paso-1"])
    return html.Div(
        className="lv-eco-detalle-contenido",
        children=[
            html.Strong(titulo, className="lv-eco-detalle-titulo"),
            html.P(descripcion),
        ],
    )


def crear_ciclo_ecosistema():
    """Crea el diagrama dirigido de cuatro etapas."""
    return html.Section(
        className="lv-eco-panel-ciclo",
        children=[
            html.H3("El ciclo depredador–presa"),
            html.P(
                "Selecciona un nodo para explorar cada etapa.",
                className="lv-eco-instruccion",
            ),
            cyto.Cytoscape(
                id="lv-eco-grafo",
                elements=crear_elementos_ciclo(),
                stylesheet=ESTILO_BASE,
                layout={"name": "preset", "fit": True, "padding": 18},
                className="lv-eco-grafo",
                style={"width": "100%", "height": "325px"},
                userZoomingEnabled=False,
                userPanningEnabled=False,
                autoungrabify=True,
                boxSelectionEnabled=False,
            ),
            # La explicacion del nodo seleccionado aparece en la columna derecha.
        ],
    )


def crear_contenido_ecosistema():
    """Cuerpo del modal; se inserta en el dbc.Modal existente."""
    return html.Div(
        className="lv-eco",
        children=[
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
                                        "ETAPA SELECCIONADA",
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
                                    html.P(
                                        "Supone alimento ilimitado para las presas "
                                        "y que los zorros solo se alimentan de ellas. "
                                        "No considera migraciones, enfermedades "
                                        "ni estaciones."
                                    ),
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
    """Vincula la selección del nodo con los estilos y la explicación."""

    @app.callback(
        Output("lv-eco-grafo", "elements"),
        Output("lv-eco-detalle", "children"),
        Input("lv-eco-grafo", "tapNodeData"),
        prevent_initial_call=True,
    )
    def actualizar_etapa_ecosistema(datos_nodo):
        paso = (datos_nodo or {}).get("id", "paso-1")
        if paso not in ETAPAS:
            paso = "paso-1"
        return crear_elementos_ciclo(paso), crear_detalle_ciclo(paso)
