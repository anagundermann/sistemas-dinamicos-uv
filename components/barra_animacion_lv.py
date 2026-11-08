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


def preparar_datos_animacion(tiempo, presas, depredadores):
    """Prepara los fotogramas y los rangos a partir de UNA solucion existente.

    La integracion con solve_ivp se realiza solo en actualizar_laboratorio.
    El margen del 10 % depende de la amplitud completa de cada poblacion.
    """
    tiempo = np.asarray(tiempo, dtype=float)
    presas = np.asarray(presas, dtype=float)
    depredadores = np.asarray(depredadores, dtype=float)

    if not (
        tiempo.ndim == presas.ndim == depredadores.ndim == 1
        and len(tiempo) >= 2
        and len(tiempo) == len(presas) == len(depredadores)
        and np.all(np.diff(tiempo) > 0)
    ):
        raise ValueError(
            "La simulacion debe devolver series de igual longitud y tiempos crecientes."
        )
    if not (
        np.isfinite(tiempo).all()
        and np.isfinite(presas).all()
        and np.isfinite(depredadores).all()
    ):
        raise ValueError("La simulacion contiene valores no finitos.")

    # Una sola solucion, con dos resoluciones de visualizacion.
    tiempos_fotogramas = np.linspace(tiempo[0], tiempo[-1], NUM_FOTOGRAMAS)
    presas_fotogramas = np.interp(tiempos_fotogramas, tiempo, presas)
    depredadores_fotogramas = np.interp(tiempos_fotogramas, tiempo, depredadores)

    tiempos_curva = np.linspace(tiempo[0], tiempo[-1], 401)
    presas_curva = np.interp(tiempos_curva, tiempo, presas)
    depredadores_curva = np.interp(tiempos_curva, tiempo, depredadores)

    # Un margen del 10 % sobre el recorrido total observado en la solucion.
    def rango_poblacion(valores):
        minimo = float(np.min(valores))
        maximo = float(np.max(valores))
        amplitud = maximo - minimo
        margen = 0.10 * amplitud if amplitud > 0 else max(1.0, 0.10 * abs(maximo))
        # Solo es un margen del eje: no modifica los datos del modelo.
        # Se permite un limite visual negativo para separar la curva del borde.
        return [minimo - margen, maximo + margen]

    poblaciones_juntas = np.concatenate((presas, depredadores))
    duracion = float(tiempo[-1] - tiempo[0])
    return {
        # Se conserva la solucion original de 801 muestras como fuente comun.
        "tiempo_completo": tiempo.tolist(),
        "presas_completas": presas.tolist(),
        "depredadores_completos": depredadores.tolist(),
        "t": tiempos_fotogramas.tolist(),
        "x": presas_fotogramas.tolist(),
        "y": depredadores_fotogramas.tolist(),
        "t_curva": tiempos_curva.tolist(),
        "x_curva": presas_curva.tolist(),
        "y_curva": depredadores_curva.tolist(),
        # Dejar un 10 % antes de t=0 y despues de t=40.
        # Asi la linea t=0 se separa de los numeros del eje vertical.
        "rango_t": [
            float(tiempo[0]) - 0.10 * duracion,
            float(tiempo[-1]) + 0.10 * duracion,
        ],
        "rango_poblacion": rango_poblacion(poblaciones_juntas),
        "rango_x_fases": rango_poblacion(presas),
        "rango_y_fases": rango_poblacion(depredadores),
    }


def crear_formas_guia(t, x, y, datos, activa):
    """Genera guias sincronizadas sin alterar limites ni datos numericos.

    La guia temporal sigue t. Las proyecciones del plano de fases
    llegan al borde inferior e izquierdo del area de dibujo.
    """
    if not activa or not datos:
        return [], []

    t, x, y = float(t), float(x), float(y)
    x_min = float(datos["rango_x_fases"][0])
    y_min = float(datos["rango_y_fases"][0])
    estilo = {"color": "rgba(234, 88, 12, 0.72)", "width": 1.5, "dash": "dot"}

    guia_tiempo = [
        {
            "type": "line",
            "xref": "x",
            "yref": "paper",
            "x0": t,
            "x1": t,
            "y0": 0,
            "y1": 1,
            "line": estilo,
            "layer": "above",
        }
    ]
    guias_fases = [
        {
            "type": "line",
            "xref": "x",
            "yref": "y",
            "x0": x_min,
            "x1": x,
            "y0": y,
            "y1": y,
            "line": estilo,
            "layer": "below",
        },
        {
            "type": "line",
            "xref": "x",
            "yref": "y",
            "x0": x,
            "x1": x,
            "y0": y_min,
            "y1": y,
            "line": estilo,
            "layer": "below",
        },
    ]
    return guia_tiempo, guias_fases


def crear_anotaciones_guia(x, y, datos, activa):
    """Muestra las coordenadas de la proyeccion dentro del plano de fases.

    Las etiquetas viven dentro del area del grafico, sin afectar escalas,
    leyendas, titulos o margenes. Se eliminan junto con la Guia.
    """
    if not activa or not datos:
        return []

    x = float(x)
    y = float(y)
    x_min, x_max = map(float, datos["rango_x_fases"])
    y_min, y_max = map(float, datos["rango_y_fases"])
    fraccion_x = (x - x_min) / max(x_max - x_min, 1e-12)
    fraccion_y = (y - y_min) / max(y_max - y_min, 1e-12)

    # Para estados proximos al borde, abrir las etiquetas hacia el interior.
    ancla_x = (
        "left" if fraccion_x < 0.10 else "right" if fraccion_x > 0.90 else "center"
    )
    desplazamiento_x = 5 if ancla_x == "left" else -5 if ancla_x == "right" else 0
    cerca_arriba = fraccion_y > 0.88

    estilo = {
        "showarrow": False,
        "font": {"family": "Arial, sans-serif", "size": 11, "color": "#C2410C"},
        "bgcolor": "rgba(255, 241, 229, 0.97)",
        "bordercolor": "rgba(251, 146, 60, 0.50)",
        "borderwidth": 1,
        "borderpad": 3,
        "captureevents": False,
    }
    return [
        {
            **estilo,
            "text": f"{x:.1f}",
            "xref": "x",
            "yref": "paper",
            "x": x,
            "y": 0,
            "xanchor": ancla_x,
            "yanchor": "bottom",
            "xshift": desplazamiento_x,
            "yshift": 6,
        },
        {
            **estilo,
            "text": f"{y:.1f}",
            "xref": "paper",
            "yref": "y",
            "x": 0,
            "y": y,
            "xanchor": "left",
            "yanchor": "top" if cerca_arriba else "bottom",
            "xshift": 7,
            "yshift": -4 if cerca_arriba else 4,
        },
    ]


def _actualizar_formas_guia(temporal, fases, t, x, y, datos, activa):
    """Sustituye solamente las capas de guias dentro de ambos Patch."""
    formas_t, formas_f = crear_formas_guia(t, x, y, datos, activa)
    temporal["layout"]["shapes"] = formas_t
    fases["layout"]["shapes"] = formas_f
    fases["layout"]["annotations"] = crear_anotaciones_guia(x, y, datos, activa)


def _estado_visible(figura_tiempo, datos):
    """Prioriza los marcadores actuales; sin ellos, parte en t=0."""
    trazas = (figura_tiempo or {}).get("data", [])
    if len(trazas) >= 4:
        try:
            t = float(_serie_de_figura(trazas[2].get("x", []))[0])
            x = float(_serie_de_figura(trazas[2].get("y", []))[0])
            y = float(_serie_de_figura(trazas[3].get("y", []))[0])
            if np.isfinite([t, x, y]).all():
                return t, x, y
        except (ValueError, TypeError, IndexError, KeyError):
            pass
    if datos and datos.get("tiempo_completo"):
        return (
            float(datos["tiempo_completo"][0]),
            float(datos["presas_completas"][0]),
            float(datos["depredadores_completos"][0]),
        )
    return None


def _parche_marcador_fases(figura_fases, x, y):
    """Crea o mueve el marcador de estado actual en el plano de fases."""
    parche = Patch()
    trazas = (figura_fases or {}).get("data", [])
    if len(trazas) < 4:
        parche["data"].append(
            {
                "type": "scatter",
                "mode": "markers",
                "showlegend": True,
                "name": "Estado actual",
                "x": [float(x)],
                "y": [float(y)],
                "marker": {
                    "size": 12,
                    "color": "#C0267D",
                    "line": {"color": "#FFFFFF", "width": 2},
                },
                "hoverinfo": "skip",
            }
        )
    else:
        parche["data"][3]["x"] = [float(x)]
        parche["data"][3]["y"] = [float(y)]
        parche["data"][3]["showlegend"] = True
        parche["data"][3]["name"] = "Estado actual"
    return parche


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


# para suavidad del palno de dfase


def _crear_parches(datos, n, figura_fases, figura_tiempo=None, guia_activa=False):
    """Actualiza los graficos usando una trayectoria de fases mas detallada."""
    limite = min(max(int(n or 0), 0), len(datos["t"]) - 1) + 1
    t = datos["t"][:limite]
    x = datos["x"][:limite]
    y = datos["y"][:limite]
    # Grafico temporal: conserva los 120 fotogramas.
    temporal = _parche_marcadores_temporales(figura_tiempo, t[-1], x[-1], y[-1])
    temporal["data"][0]["x"] = t
    temporal["data"][0]["y"] = x
    temporal["data"][1]["x"] = t
    temporal["data"][1]["y"] = y
    # Plano de fases: dibuja mas puntos hasta el instante actual.
    tiempos_curva = np.asarray(datos["t_curva"], dtype=float)
    hasta = int(np.searchsorted(tiempos_curva, t[-1], side="right"))
    x_curva = datos["x_curva"][:hasta].copy()
    y_curva = datos["y_curva"][:hasta].copy()
    # Asegura que la curva termine exactamente en el marcador.
    if hasta == 0 or not np.isclose(
        tiempos_curva[hasta - 1],
        t[-1],
        atol=1e-10,
        rtol=0,
    ):
        x_curva.append(x[-1])
        y_curva.append(y[-1])
    fases = _parche_marcador_fases(figura_fases, x[-1], y[-1])
    fases["data"][0]["x"] = x_curva
    fases["data"][0]["y"] = y_curva
    _actualizar_formas_guia(temporal, fases, t[-1], x[-1], y[-1], datos, guia_activa)
    # Conserva la actualizacion del mini panel de poblaciones.
    return (
        temporal,
        fases,
        f"t = {float(t[-1]):.1f}",
        f"{float(x[-1]):.1f}",
        f"{float(y[-1]):.1f}",
    )


@callback(
    Output(ID_RELOJ, "disabled"),
    Output(ID_RELOJ, "interval"),
    Output(ID_RELOJ, "n_intervals"),
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
    Input(ID_DATOS, "data"),
    State(ID_RELOJ, "n_intervals"),
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
    datos,
    posicion,
):
    accion = ctx.triggered_id
    intervalo = _intervalo(velocidad)

    if accion in CONTROLES_PARAMETROS or accion == ID_DATOS:
        # Una solucion nueva reemplaza la anterior: detener y volver a t=0.
        return True, intervalo, 0
    if accion == ID_PAUSA:
        return True, no_update, no_update
    if accion == ID_REINICIAR:
        return True, no_update, 0
    if accion == ID_VELOCIDAD:
        return no_update, intervalo, no_update
    if accion == ID_PLAY:
        if not datos or not datos.get("t"):
            raise PreventUpdate
        if (posicion or 0) >= len(datos["t"]) - 1:
            posicion = 0
        # Solo reproduce el cache: nunca ejecuta solve_ivp.
        return False, intervalo, posicion or 0
    raise PreventUpdate


@callback(
    Output("lv-grafico-tiempo", "figure", allow_duplicate=True),
    Output("lv-grafico-fases", "figure", allow_duplicate=True),
    Output("lv-estado-tiempo", "children", allow_duplicate=True),
    Output("lv-estado-presas", "children", allow_duplicate=True),
    Output("lv-estado-depredadores", "children", allow_duplicate=True),
    Input(ID_RELOJ, "n_intervals"),
    Input(ID_DATOS, "data"),
    Input("lv-grafico-tiempo", "hoverData"),
    Input(ID_REINICIAR, "n_clicks"),
    State("lv-grafico-fases", "figure"),
    State("lv-grafico-tiempo", "figure"),
    State(ID_RELOJ, "disabled"),
    State("lv-guia-vertical", "value"),
    prevent_initial_call=True,
)
def mostrar_fotograma(
    n_intervals,
    datos,
    hover_data,
    n_reiniciar,
    figura_fases,
    figura_tiempo,
    esta_pausado,
    guia_activa,
):
    """Los cursores usan el cache. No alteran las escalas de los graficos."""
    accion = ctx.triggered_id

    # No iniciar una animacion al llegar una solucion nueva al Store.
    # Los graficos completos ya son actualizados por la pagina principal.
    if accion == ID_DATOS:
        raise PreventUpdate

    if accion == ID_REINICIAR:
        if datos is None:
            raise PreventUpdate
        return _crear_parches(datos, 0, figura_fases, figura_tiempo, guia_activa)

    if accion == "lv-grafico-tiempo":
        # Durante Play tiene prioridad el reloj; cuando esta pausado se
        # permite explorar manualmente cualquier instante visible.
        terminado = datos is not None and n_intervals >= len(datos["t"]) - 1
        if not esta_pausado and not terminado:
            raise PreventUpdate
        punto = _obtener_puntos_hover(hover_data, figura_tiempo)
        if punto is None:
            raise PreventUpdate
        temporal = _parche_marcadores_temporales(figura_tiempo, *punto)
        fases = _parche_marcador_fases(figura_fases, punto[1], punto[2])
        _actualizar_formas_guia(
            temporal, fases, punto[0], punto[1], punto[2], datos, guia_activa
        )
        return (
            temporal,
            fases,
            f"t = {float(punto[0]):.1f}",
            f"{float(punto[1]):.1f}",
            f"{float(punto[2]):.1f}",
        )
    if datos is None or esta_pausado:
        raise PreventUpdate
    return _crear_parches(datos, n_intervals, figura_fases, figura_tiempo, guia_activa)
