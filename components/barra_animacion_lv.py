"""Barra compacta y animacion sincronizada de Lotka-Volterra.

Solo usa Dash, dash-bootstrap-components, numpy y el modelo ya existente.
La pagina principal mantiene sus graficos, sus estilos y sus callbacks.
Agrega dos marcadores sincronizados que siguen el cursor del mouse o el Play.
Los callbacks se registran mediante @dash.callback cuando este modulo se importa.
La pagina ya importa crear_barra_animacion_vista_previa; no editarla.
"""

import base64

import numpy as np
from dash import Input, Output, Patch, State, callback, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from models.modelo_lotka_volterra import simular_lotka_volterra


# A 1x, 120 cuadros cada 140 ms: aproximadamente 17 segundos.
NUM_FOTOGRAMAS = 120
INTERVALO_BASE_MS = 140
VELOCIDADES = {"0.5": 0.5, "1": 1.0, "1.5": 1.5, "2": 2.0}

ID_PLAY = "lv-animacion-play"
ID_PAUSA = "lv-animacion-pausa"
ID_REINICIAR = "lv-animacion-reiniciar"
ID_VELOCIDAD = "lv-animacion-velocidad"
ID_RELOJ = "lv-animacion-reloj"
ID_DATOS = "lv-animacion-datos"

CONTROLES_PARAMETROS = (
    "lv-alpha",
    "lv-beta",
    "lv-gamma",
    "lv-delta",
    "lv-presas-0",
    "lv-depredadores-0",
)


def crear_barra_animacion():
    """Botones operativos, conservando las clases CSS de la vista previa."""
    return html.Div(
        className="lv-animacion-vista",
        children=[
            html.Span("Animación", className="lv-animacion-titulo"),
            html.Div(
                className="lv-animacion-fila",
                children=[
                    html.Button(
                        "▶",
                        id=ID_PLAY,
                        n_clicks=0,
                        type="button",
                        className="lv-animacion-boton",
                        title="Reproducir los dos gráficos",
                        **{"aria-label": "Reproducir animación"},
                    ),
                    html.Button(
                        "❚❚",
                        id=ID_PAUSA,
                        n_clicks=0,
                        type="button",
                        className="lv-animacion-boton",
                        title="Pausar la animación",
                        **{"aria-label": "Pausar animación"},
                    ),
                    html.Button(
                        "↺",
                        id=ID_REINICIAR,
                        n_clicks=0,
                        type="button",
                        className="lv-animacion-boton",
                        title="Volver al inicio y pausar",
                        **{"aria-label": "Reiniciar animación"},
                    ),
                    html.Label(
                        "Vel.",
                        htmlFor=ID_VELOCIDAD,
                        className="lv-animacion-etiqueta",
                    ),
                    dbc.Select(
                        id=ID_VELOCIDAD,
                        class_name="lv-animacion-select",
                        value="1",
                        options=[
                            {"label": "0.5×", "value": "0.5"},
                            {"label": "1×", "value": "1"},
                            {"label": "1.5×", "value": "1.5"},
                            {"label": "2×", "value": "2"},
                        ],
                        size="sm",
                    ),
                ],
            ),
            dcc.Interval(
                id=ID_RELOJ,
                interval=INTERVALO_BASE_MS,
                n_intervals=0,
                max_intervals=NUM_FOTOGRAMAS - 1,
                disabled=True,
            ),
            dcc.Store(id=ID_DATOS, data=None, storage_type="memory"),
        ],
    )


def crear_barra_animacion_vista_previa():
    """Nombre compatible con la importacion ya instalada (ahora operativo)."""
    return crear_barra_animacion()


def _intervalo(velocidad):
    return round(INTERVALO_BASE_MS / VELOCIDADES.get(str(velocidad), 1.0))


def _serie_simulacion(alpha, beta, gamma, delta, presas_0, depredadores_0):
    """Calcula UNA VEZ al pulsar Play; prepara una muestra ligera para el navegador."""
    tiempo, presas, depredadores = simular_lotka_volterra(
        alpha, beta, gamma, delta, presas_0, depredadores_0
    )
    tiempo = np.asarray(tiempo, dtype=float)
    presas = np.asarray(presas, dtype=float)
    depredadores = np.asarray(depredadores, dtype=float)

    if tiempo.ndim != 1 or len(tiempo) < 2 or np.any(np.diff(tiempo) <= 0):
        raise ValueError(
            "La simulacion debe devolver tiempos estrictamente crecientes."
        )
    if not (
        np.isfinite(tiempo).all()
        and np.isfinite(presas).all()
        and np.isfinite(depredadores).all()
    ):
        raise ValueError("La simulacion contiene valores no finitos.")

    nuevos_tiempos = np.linspace(tiempo[0], tiempo[-1], NUM_FOTOGRAMAS)
    nuevas_presas = np.interp(nuevos_tiempos, tiempo, presas)
    nuevos_depredadores = np.interp(nuevos_tiempos, tiempo, depredadores)

    # Limites de los ejes calculados con la solucion completa para evitar
    # que Plotly cambie la escala cuando se va dibujando la trayectoria.
    minimo = float(min(presas.min(), depredadores.min()))
    maximo = float(max(presas.max(), depredadores.max()))
    margen_y = max(2.0, (maximo - minimo) * 0.09)

    margen_x_fases = max(2.0, float(np.ptp(presas)) * 0.10)
    margen_y_fases = max(2.0, float(np.ptp(depredadores)) * 0.10)

    return {
        "t": nuevos_tiempos.tolist(),
        "x": nuevas_presas.tolist(),
        "y": nuevos_depredadores.tolist(),
        "rango_t": [float(tiempo[0]), float(tiempo[-1])],
        "rango_poblacion": [max(0.0, minimo - margen_y), maximo + margen_y],
        "rango_x_fases": [
            float(presas.min()) - margen_x_fases,
            float(presas.max()) + margen_x_fases,
        ],
        "rango_y_fases": [
            float(depredadores.min()) - margen_y_fases,
            float(depredadores.max()) + margen_y_fases,
        ],
    }


def _traza_marcador(nombre, color, x, y):
    """Un solo punto, sin entrada adicional en la leyenda o el tooltip."""
    return {
        "type": "scatter",
        "mode": "markers",
        "name": nombre,
        "x": [float(x)],
        "y": [float(y)],
        "showlegend": False,
        "hoverinfo": "skip",
        "marker": {
            "size": 10,
            "color": color,
            "line": {"color": "#FFFFFF", "width": 1.8},
        },
    }


def _parche_marcadores_temporales(figura_tiempo, t, x, y):
    """Crea ambos puntos una vez y luego actualiza solo sus coordenadas."""
    parche = Patch()
    trazas = (figura_tiempo or {}).get("data", [])
    marcadores = (
        _traza_marcador("Cursor · Presas", "#14B8A6", t, x),
        _traza_marcador("Cursor · Depredadores", "#7C3AED", t, y),
    )
    for indice, marcador in enumerate(marcadores, start=2):
        if indice < len(trazas):
            parche["data"][indice]["x"] = marcador["x"]
            parche["data"][indice]["y"] = marcador["y"]
        else:
            parche["data"].append(marcador)
    return parche


def _serie_de_figura(datos):
    """Lee arrays normales o arrays binarios serializados por Plotly 6."""
    if isinstance(datos, dict) and "bdata" in datos:
        tipo = np.dtype(datos.get("dtype", "f8"))
        valores = np.frombuffer(base64.b64decode(datos["bdata"]), dtype=tipo)
        return valores.reshape(datos["shape"]) if "shape" in datos else valores
    return np.asarray(datos, dtype=float)


def _obtener_puntos_hover(hover_data, figura_tiempo):
    """Ubica presas y depredadores en el MISMO instante seleccionado."""
    puntos = (hover_data or {}).get("points") or []
    por_traza = {
        p.get("curveNumber"): p
        for p in puntos
        if p.get("curveNumber") in (0, 1) and "x" in p
    }
    if not por_traza:
        return None
    t = float(next(iter(por_traza.values()))["x"])
    if not np.isfinite(t):
        return None

    trazas = (figura_tiempo or {}).get("data") or []
    if len(trazas) < 2:
        return None

    valores = []
    for indice in (0, 1):
        punto = por_traza.get(indice)
        if punto is not None and "y" in punto and abs(float(punto["x"]) - t) < 1e-7:
            valores.append(float(punto["y"]))
            continue

        # Algunos navegadores envian solo la traza mas proxima al cursor.
        # Obtenemos la segunda poblacion de los datos ya mostrados.
        tiempos = _serie_de_figura(trazas[indice].get("x", []))
        poblaciones = _serie_de_figura(trazas[indice].get("y", []))
        if not len(tiempos) or len(tiempos) != len(poblaciones):
            return None
        cercano = int(np.abs(tiempos - t).argmin())
        valores.append(float(poblaciones[cercano]))

    if not all(np.isfinite(valor) for valor in valores):
        return None
    return t, valores[0], valores[1]


def _crear_parches(datos, n, figura_fases, figura_tiempo=None):
    """Actualiza las curvas y los marcadores; no reconstruye los graficos."""
    limite = min(max(int(n or 0), 0), len(datos["t"]) - 1) + 1
    t = datos["t"][:limite]
    x = datos["x"][:limite]
    y = datos["y"][:limite]

    temporal = _parche_marcadores_temporales(figura_tiempo, t[-1], x[-1], y[-1])
    temporal["data"][0]["x"] = t
    temporal["data"][0]["y"] = x
    temporal["data"][1]["x"] = t
    temporal["data"][1]["y"] = y
    temporal["layout"]["xaxis"]["range"] = datos["rango_t"]
    temporal["layout"]["yaxis"]["range"] = datos["rango_poblacion"]

    fases = Patch()
    fases["data"][0]["x"] = x
    fases["data"][0]["y"] = y
    fases["layout"]["xaxis"]["range"] = datos["rango_x_fases"]
    fases["layout"]["yaxis"]["range"] = datos["rango_y_fases"]

    # Conserva las marcas de inicio y equilibrio. El cuarto trazo rosa
    # sigue el mismo instante que las dos bolitas del grafico temporal.
    if len((figura_fases or {}).get("data", [])) < 4:
        fases["data"].append(
            {
                "type": "scatter",
                "mode": "markers",
                "showlegend": False,
                "name": "Posición actual",
                "x": [x[-1]],
                "y": [y[-1]],
                "marker": {
                    "size": 12,
                    "color": "#C0267D",
                    "line": {"color": "#FFFFFF", "width": 2},
                },
                "hovertemplate": "Presas: %{x:.1f}<br>Depredadores: %{y:.1f}<extra></extra>",
            }
        )
    else:
        fases["data"][3]["x"] = [x[-1]]
        fases["data"][3]["y"] = [y[-1]]

    return temporal, fases


@callback(
    Output(ID_RELOJ, "disabled"),
    Output(ID_RELOJ, "interval"),
    Output(ID_RELOJ, "n_intervals"),
    Output(ID_DATOS, "data"),
    Input(ID_PLAY, "n_clicks"),
    Input(ID_PAUSA, "n_clicks"),
    Input(ID_REINICIAR, "n_clicks"),
    Input(ID_VELOCIDAD, "value"),
    Input("lv-alpha", "value"),
    Input("lv-beta", "value"),
    Input("lv-gamma", "value"),
    Input("lv-delta", "value"),
    Input("lv-presas-0", "value"),
    Input("lv-depredadores-0", "value"),
    State(ID_RELOJ, "n_intervals"),
    State(ID_DATOS, "data"),
    prevent_initial_call=True,
)
def controlar_animacion(
    n_play,
    n_pausa,
    n_reiniciar,
    velocidad,
    alpha,
    beta,
    gamma,
    delta,
    presas_0,
    depredadores_0,
    posicion,
    datos,
):
    accion = ctx.triggered_id
    intervalo = _intervalo(velocidad)

    if accion in CONTROLES_PARAMETROS:
        # El callback original regenera las figuras completas con los
        # nuevos parametros. Se invalida cualquier animacion anterior.
        return True, intervalo, 0, None

    if accion == ID_PAUSA:
        return True, no_update, no_update, no_update

    if accion == ID_REINICIAR:
        # Volver a t=0 y permanecer en pausa.
        return True, no_update, 0, no_update

    if accion == ID_VELOCIDAD:
        return no_update, intervalo, no_update, no_update

    if accion == ID_PLAY:
        if datos is None:
            datos = _serie_simulacion(
                alpha, beta, gamma, delta, presas_0, depredadores_0
            )
            posicion = 0
        elif (posicion or 0) >= len(datos["t"]) - 1:
            posicion = 0  # Reproducir nuevamente al terminar.
        return False, intervalo, posicion or 0, datos

    raise PreventUpdate


@callback(
    Output("lv-grafico-tiempo", "figure", allow_duplicate=True),
    Output("lv-grafico-fases", "figure", allow_duplicate=True),
    Input(ID_RELOJ, "n_intervals"),
    Input(ID_DATOS, "data"),
    Input("lv-grafico-tiempo", "hoverData"),
    State("lv-grafico-fases", "figure"),
    State("lv-grafico-tiempo", "figure"),
    State(ID_RELOJ, "disabled"),
    prevent_initial_call=True,
)
def mostrar_fotograma(
    n_intervals, datos, hover_data, figura_fases, figura_tiempo, esta_pausado
):
    """Usa los mismos marcadores con el mouse y durante la animacion."""
    if ctx.triggered_id == "lv-grafico-tiempo":
        # Durante Play tiene prioridad el reloj; cuando esta pausado se
        # permite explorar manualmente cualquier instante visible.
        terminado = datos is not None and n_intervals >= len(datos["t"]) - 1
        if not esta_pausado and not terminado:
            raise PreventUpdate
        punto = _obtener_puntos_hover(hover_data, figura_tiempo)
        if punto is None:
            raise PreventUpdate
        return _parche_marcadores_temporales(figura_tiempo, *punto), no_update

    if datos is None:
        raise PreventUpdate
    return _crear_parches(datos, n_intervals, figura_fases, figura_tiempo)
