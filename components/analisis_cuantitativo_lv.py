"""Analisis cuantitativo de Lotka-Volterra (clasico y logistico).

La pagina principal ya importa estas tres funciones:
    crear_boton_analisis_lv
    crear_modal_analisis_lv
    registrar_callbacks_analisis_lv

Solo consulta los resultados de lv-animacion-datos. No modifica Play.
"""

from urllib.parse import quote
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, ctx, dcc, html
import dash_bootstrap_components as dbc


# ============================================================
# AJUSTES DE DISENO: MODIFICA SOLO ESTOS VALORES SI LO NECESITAS
# ============================================================

ANCHO_CONTENIDO = 990  # px: determina tambien el ancho del modal
PADDING_MODAL = 18  # px: espacio a izquierda y derecha
ANCHO_DESLIZADOR = "94%"  # "100%", "94%", "85%", etc.

# Proporcion de las dos columnas de cada fila:
PROPORCION_VARIACION = 1.0
PROPORCION_TASA = 1.0
PROPORCION_DISTANCIA = 1.10
PROPORCION_INTERPRETACION = 0.90
SEPARACION_COLUMNAS = 16  # px

# Ancho de los rectangulos que contienen SOLO los resultados:
ANCHO_TARJETA_VARIACION = 190  # px
ANCHO_TARJETA_TASA = 148  # px
ANCHO_TARJETA_DISTANCIA = 130  # px

TAMANO_FORMULA = 16  # px, orientativo: el tamano real depende de MathJax

AZUL = "#183153"
GRIS = "#65748b"
BORDE = "#dfe7f0"
PRESAS = "#0f9f94"
DEPREDADORES = "#7c3aed"


# ============================================================
# PRESENTACION
# ============================================================


# Flechas discretas del plano de fases. False las desactiva en ambas vistas.
FLECHAS_FASE_ACTIVAS = True


def estilo_flechas_fase(presas, depredadores, cantidad=2, tamano=12, color="#486A80"):
    """Configura flechas tangentes sobre la traza existente, sin agregar trazas.

    Plotly orienta cada marcador 'arrow' segun el segmento anterior de la
    trayectoria, que sigue el orden temporal entregado por solve_ivp.
    Los tamanos cero dejan invisibles los demas marcadores.

    Importante: esta funcion se aplica a la misma malla de la curva que
    utiliza Play (datos['x_curva'], datos['y_curva']). De esa manera, los
    marcadores conservan su posicion al actualizar la curva con Dash Patch.
    """
    sin_flechas = {"mode": "lines"}
    if not FLECHAS_FASE_ACTIVAS:
        return sin_flechas

    x = np.asarray(presas, dtype=float)
    y = np.asarray(depredadores, dtype=float)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size or x.size < 3:
        return sin_flechas
    if not (np.all(np.isfinite(x)) and np.all(np.isfinite(y))):
        return sin_flechas

    # Evita dibujar flechas falsas por ruido numerico en una solucion constante.
    tolerancia_x = 1e-7 * max(1.0, float(np.max(np.abs(x))))
    tolerancia_y = 1e-7 * max(1.0, float(np.max(np.abs(y))))
    if (
        np.max(np.abs(x - x[0])) <= tolerancia_x
        and np.max(np.abs(y - y[0])) <= tolerancia_y
    ):
        return sin_flechas

    # Elegir sitios segun la longitud del recorrido, no el indice de tiempo.
    # Normalizar por rango de cada eje para considerar ambas poblaciones.
    escala_x = max(float(np.ptp(x)), 1e-12)
    escala_y = max(float(np.ptp(y)), 1e-12)
    pasos = np.hypot(np.diff(x) / escala_x, np.diff(y) / escala_y)
    distancias = np.concatenate(([0.0], np.cumsum(pasos)))
    recorrido = float(distancias[-1])
    if not np.isfinite(recorrido) or recorrido <= 1e-9:
        return sin_flechas

    fracciones = (0.53,) if cantidad == 1 else (0.28, 0.72)
    tamanos = np.zeros(x.size, dtype=float)
    for fraccion in fracciones:
        indice = int(np.searchsorted(distancias, fraccion * recorrido))
        indice = min(max(indice, 1), x.size - 1)
        # Protegerse de segmentos degenerados y evitar flechas superpuestas.
        while indice < x.size - 1 and pasos[indice - 1] <= 1e-12:
            indice += 1
        if pasos[indice - 1] > 1e-12:
            tamanos[indice] = float(tamano)

    if not tamanos.any():
        return sin_flechas
    return {
        "mode": "lines+markers",
        "marker": {
            "symbol": "arrow",
            "angleref": "previous",
            "size": tamanos.tolist(),
            "color": color,
            "opacity": 0.9,
            "line": {"width": 0},
        },
    }


def _math(latex):
    """Formula LaTeX con espacio vertical y sin barras internas."""
    return dcc.Markdown(
        "$\\displaystyle " + latex + "$",
        mathjax=True,
        style={
            "margin": "0",
            "padding": "10px 0",
            "minWidth": 0,
            "fontSize": f"{TAMANO_FORMULA}px",
            "color": AZUL,
            "overflow": "visible",
            "maxWidth": "100%",
        },
    )


def _indicador(etiqueta, valor, formula, ancho_tarjeta, estado="", color_valor=None):
    """Tarjeta pequena a la izquierda, ecuacion por fuera a la derecha."""
    tarjeta = html.Div(
        [
            html.Div(
                etiqueta,
                style={
                    "fontSize": "12px",
                    "color": GRIS,
                    "lineHeight": "1.2",
                },
            ),
            html.Div(
                valor,
                style={
                    "fontSize": "23px",
                    "fontWeight": 800,
                    "lineHeight": "1.2",
                    "color": color_valor or AZUL,
                    "marginTop": "4px",
                },
            ),
            html.Div(
                [
                    html.Img(
                        src="data:image/svg+xml,"
                        + quote(
                            '<svg xmlns="http://www.w3.org/2000/svg" '
                            'viewBox="0 0 24 24" fill="none" '
                            'stroke="#2563eb" stroke-width="2.4" '
                            'stroke-linecap="round" stroke-linejoin="round">'
                            '<polyline points="2 17 8 11 13 15 22 6"/>'
                            '<polyline points="16 6 22 6 22 12"/>'
                            "</svg>"
                            if estado == "Aumentando"
                            else '<svg xmlns="http://www.w3.org/2000/svg" '
                            'viewBox="0 0 24 24" fill="none" '
                            'stroke="#a34f18" stroke-width="2.4" '
                            'stroke-linecap="round" stroke-linejoin="round">'
                            '<polyline points="2 7 8 13 13 9 22 18"/>'
                            '<polyline points="16 18 22 18 22 12"/>'
                            "</svg>"
                        ),
                        style={
                            "width": "17px",
                            "height": "17px",
                            "flexShrink": 0,
                        },
                    )
                    if estado in ("Aumentando", "Disminuyendo")
                    else html.Span(
                        "→",
                        style={"fontSize": "17px", "lineHeight": "1"},
                    )
                    if estado == "Variación casi nula"
                    else None,
                    html.Span(estado),
                ],
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "6px",
                    "fontSize": "12px",
                    "fontWeight": 700,
                    "color": (
                        "#a34f18"
                        if estado == "Disminuyendo"
                        else "#2563eb"
                        if estado == "Aumentando"
                        else GRIS
                    ),
                    "marginTop": "3px",
                },
            )
            if estado
            else None,
        ],
        style={
            "width": f"{ancho_tarjeta}px",
            "maxWidth": "100%",
            "border": f"1px solid {BORDE}",
            "borderRadius": "10px",
            "padding": "10px 12px",
            "minHeight": "76px",
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "center",
            "backgroundColor": "#fff",
        },
    )
    return html.Div(
        [
            tarjeta,
            html.Div(
                _math(formula),
                style={
                    "minWidth": 0,
                    "minHeight": "95px",
                    "display": "flex",
                    "alignItems": "center",
                    "overflow": "visible",
                    "padding": "8px 0",
                },
            ),
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": f"minmax(0, {ancho_tarjeta}px) minmax(0, 1fr)",
            "gap": "10px",
            "alignItems": "center",
            "minWidth": 0,
        },
    )


def _seccion(titulo, variacion, tasa):
    """Una sola fila con dos columnas: variacion | tasa."""
    return html.Section(
        [
            html.H3(
                titulo,
                style={
                    "margin": "0 0 8px",
                    "paddingBottom": "5px",
                    "fontSize": "16px",
                    "fontWeight": 750,
                    "color": PRESAS if titulo == "Presas" else DEPREDADORES,
                    "borderBottom": f"1px solid {BORDE}",
                },
            ),
            html.Div(
                [variacion, tasa],
                style={
                    "display": "grid",
                    "gridTemplateColumns": (
                        f"minmax(0, {PROPORCION_VARIACION}fr) "
                        f"minmax(0, {PROPORCION_TASA}fr)"
                    ),
                    "columnGap": f"{SEPARACION_COLUMNAS}px",
                    "minWidth": 0,
                },
            ),
        ],
        style={"marginBottom": "14px", "minWidth": 0},
    )


def _interpretacion():
    def fila(simbolo, frase):
        return html.Div(
            [
                html.Strong(simbolo, style={"color": AZUL}),
                " · " + frase,
            ],
            style={"fontSize": "12px", "lineHeight": "1.5"},
        )

    return html.Div(
        [
            html.H3(
                "Interpretación de las tasas",
                style={
                    "fontSize": "16px",
                    "fontWeight": 750,
                    "color": AZUL,
                    "margin": "0 0 7px",
                },
            ),
            fila("x′(t) > 0", "Las presas aumentan"),
            fila("x′(t) < 0", "Las presas disminuyen"),
            fila("y′(t) > 0", "Los depredadores aumentan"),
            fila("y′(t) < 0", "Los depredadores disminuyen"),
            html.Div(
                "≈ 0: el valor absoluto de la tasa es menor que 0.0005 "
                "y se mostraría como 0.000 por redondeo. Puede indicar "
                "un extremo local o un cambio muy lento; no implica equilibrio.",
                style={"fontSize": "11px", "color": GRIS, "marginTop": "5px"},
            ),
        ],
        style={"minWidth": 0},
    )


def _parte_inferior(distancia, nombre_equilibrio):
    return html.Div(
        [
            html.Div(
                [
                    html.H3(
                        "Distancia relativa al equilibrio",
                        style={
                            "fontSize": "16px",
                            "fontWeight": 750,
                            "color": AZUL,
                            "margin": "0 0 7px",
                        },
                    ),
                    distancia,
                ],
                style={"minWidth": 0},
            ),
            _interpretacion(),
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": (
                f"minmax(0, {PROPORCION_DISTANCIA}fr) "
                f"minmax(0, {PROPORCION_INTERPRETACION}fr)"
            ),
            "columnGap": f"{SEPARACION_COLUMNAS}px",
            "borderTop": f"1px solid {BORDE}",
            "paddingTop": "12px",
            "minWidth": 0,
        },
    )


def _metrica(titulo, valor):
    """Tarjeta con color segun la poblacion asociada."""

    texto = str(titulo).lower()

    es_presa = "presas" in texto
    es_depredador = "depredadores" in texto

    if es_presa and not es_depredador:
        color_valor = PRESAS
    elif es_depredador and not es_presa:
        color_valor = DEPREDADORES
    else:
        color_valor = AZUL

    color_etiqueta = color_valor if color_valor != AZUL else GRIS

    return html.Div(
        [
            html.Div(
                titulo,
                style={
                    "fontSize": "12px",
                    "color": color_etiqueta,
                },
            ),
            html.Div(
                valor,
                style={
                    "fontSize": "20px",
                    "fontWeight": 700,
                    "color": color_valor,
                },
            ),
        ],
        className="lv-metrica-completa",
        style={
            "border": f"1px solid {BORDE}",
            "borderRadius": "10px",
            "padding": "9px 12px",
            "minWidth": 0,
        },
    )


def _detalle_completo(titulo, valor, formula, sustitucion):
    """Solo se usa en la pestana Simulacion completa."""
    return html.Div(
        [
            _metrica(titulo, valor),
            html.Div(
                [_math(formula), _math(sustitucion)],
                style={
                    "minWidth": 0,
                    "overflowX": "auto",
                    "alignSelf": "center",
                },
            ),
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": "185px minmax(0, 1fr)",
            "gap": "12px",
            "alignItems": "center",
            "marginBottom": "10px",
        },
    )


def crear_boton_analisis_lv():
    return html.Button(
        "Análisis de la dinámica",
        id="lv-abrir-analisis",
        className="lv-boton-analisis-inferior",
        n_clicks=0,
        type="button",
        title="Consultar los resultados matemáticos",
    )


def crear_modal_analisis_lv():
    """El ancho del modal sigue ANCHO_CONTENIDO y PADDING_MODAL."""
    ancho_modal = ANCHO_CONTENIDO + 2 * PADDING_MODAL
    return dbc.Modal(
        [
            dbc.ModalHeader(
                dbc.ModalTitle("Análisis de la dinámica"),
                close_button=True,
            ),
            dbc.ModalBody(
                [
                    dbc.RadioItems(
                        id="lv-analisis-vista",
                        options=[
                            {"label": "En un instante", "value": "instante"},
                            {"label": "Simulación completa", "value": "completa"},
                        ],
                        value="instante",
                        inline=True,
                        class_name="mb-2",
                    ),
                    html.Div(
                        [
                            html.Div(
                                id="lv-analisis-tiempo",
                                style={
                                    "fontWeight": 600,
                                    "fontSize": "14px",
                                    "marginBottom": "10px",
                                },
                            ),
                            html.Div(
                                dcc.Slider(
                                    id="lv-analisis-slider",
                                    min=0,
                                    max=40,
                                    step=0.05,
                                    value=0,
                                    marks={
                                        0: "0",
                                        10: "10",
                                        20: "20",
                                        30: "30",
                                        40: "40",
                                    },
                                    updatemode="drag",
                                ),
                                style={
                                    "width": ANCHO_DESLIZADOR,
                                    "margin": "0 auto",
                                    "padding": "0 4px",
                                },
                            ),
                        ],
                        id="lv-analisis-control-tiempo",
                        style={"marginBottom": "18px"},
                    ),
                    html.Div(id="lv-analisis-resultado"),
                ],
                style={
                    "padding": f"14px {PADDING_MODAL}px 16px",
                    "minWidth": 0,
                },
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Cerrar",
                    id="lv-cerrar-analisis",
                    color="secondary",
                    outline=True,
                )
            ),
        ],
        id="lv-modal-analisis",
        is_open=False,
        centered=True,
        scrollable=True,
        class_name="lv-modal lv-modal-analisis",
        # Bootstrap usa --bs-modal-width como ancho maximo del modal.
        # Se mantiene limitado al ancho de la ventana en pantallas pequenas.
        style={"--bs-modal-width": f"min({ancho_modal}px, calc(100vw - 32px))"},
    )


# ============================================================
# CALCULOS (SE CONSERVA LA LOGICA DEL LABORATORIO)
# ============================================================


def _distancia_relativa(x, y, xeq, yeq):
    denominador = np.hypot(xeq, yeq)
    if denominador < 1e-12:
        return None
    return 100.0 * np.hypot(x - xeq, y - yeq) / denominador


def _texto_porcentaje(valor):
    return "No definida" if valor is None else f"{valor:+.1f}%"


def _formula_distancia():
    return (
        r"D_{\mathrm{rel}}(t)="
        r"\frac{\sqrt{(x(t)-x^*)^2+(y(t)-y^*)^2}}"
        r"{\sqrt{(x^*)^2+(y^*)^2}}\cdot100\%"
    )


def _formula_variacion(variable):
    return (
        rf"\Delta_{{{variable}}}(t)="
        rf"\frac{{{variable}(t)-{variable}_0}}{{{variable}_0}}\cdot100\%"
    )


def _formula_dx(modelo):
    if modelo == "logistico":
        return r"x'(t)=\alpha x\left(1-\frac{x}{K}\right)-\beta xy"
    return r"x'(t)=\alpha x-\beta xy"


# El umbral coincide con la resolucion de visualizacion de tres decimales.
# Solo afecta el texto: NO modifica las derivadas ni la simulacion.
UMBRAL_TASA_VISIBLE = 0.0005


def _estado_tasa(valor):
    if abs(valor) < UMBRAL_TASA_VISIBLE:
        return "Variación casi nula"
    return "Aumentando" if valor > 0 else "Disminuyendo"


def _texto_tasa(valor):
    """Evita presentar -0.000 o +0.000 como si fueran tasas significativas."""
    return "≈ 0" if abs(valor) < UMBRAL_TASA_VISIBLE else f"{valor:+.3f}"


def _extremo_local_cercano(t, tiempos, valores):
    """Detecta extremos reales de la serie; no confunde tasa casi cero con equilibrio.

    Mantiene el criterio de prominencia usado por la pagina principal. El
    refinamiento parabolico local evita tomar el instante de la malla como
    si fuera exactamente el del extremo.
    """
    from scipy.signal import find_peaks

    if len(tiempos) < 3:
        return None
    amplitud = float(np.ptp(valores))
    escala = max(float(np.max(np.abs(valores))), 1.0)
    if amplitud < max(1e-7, 1e-7 * escala):
        return None
    prominencia = max(0.001 * amplitud, 1e-7)
    maximos, _ = find_peaks(valores, prominence=prominencia)
    minimos, _ = find_peaks(-valores, prominence=prominencia)

    pasos = np.diff(tiempos)
    pasos = pasos[pasos > 0]
    if len(pasos) == 0:
        return None
    # Una ventana de una muestra cercana, no un intervalo arbitrariamente grande.
    tolerancia = 0.8 * float(np.median(pasos))
    mejor = None
    distancia_menor = float("inf")

    for indices, tipo in ((maximos, "máximo"), (minimos, "mínimo")):
        for indice in indices:
            i = int(indice)
            if i <= 0 or i >= len(tiempos) - 1:
                continue
            tiempos_locales = tiempos[i - 1 : i + 2] - tiempos[i]
            valores_locales = valores[i - 1 : i + 2]
            coef = np.polyfit(tiempos_locales, valores_locales, 2)
            tiempo_extremo = float(tiempos[i])
            if abs(coef[0]) > 1e-14:
                desplazamiento = float(-coef[1] / (2.0 * coef[0]))
                if tiempos_locales[0] <= desplazamiento <= tiempos_locales[-1]:
                    tiempo_extremo += desplazamiento
            diferencia = abs(float(t) - tiempo_extremo)
            if diferencia <= tolerancia and diferencia < distancia_menor:
                mejor, distancia_menor = tipo, diferencia
    return mejor


def _bloque_completo(titulo, metricas, formula=None, nota=None):
    """Seccion compacta: resultados numericos y formula fuera de las tarjetas."""
    hijos = [
        html.H3(
            titulo,
            style={
                "fontSize": "16px",
                "fontWeight": 750,
                "color": AZUL,
                "margin": "0 0 9px",
                "borderBottom": f"1px solid {BORDE}",
                "paddingBottom": "6px",
            },
        ),
        html.Div(
            [_metrica(etiqueta, valor) for etiqueta, valor in metricas],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fit, minmax(170px, 1fr))",
                "gap": "10px",
                "minWidth": 0,
            },
        ),
    ]
    if formula:
        # Una formula por linea: evita comandos LaTeX pegados como \quadT.
        formulas = [formula] if isinstance(formula, str) else list(formula)
        hijos.append(
            html.Div(
                [_math(expresion) for expresion in formulas],
                style={
                    "marginTop": "3px",
                    "minWidth": 0,
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "flex-start",
                    "gap": "0px",
                },
            )
        )
    if nota:
        hijos.append(
            html.P(
                nota,
                style={
                    "fontSize": "12px",
                    "color": GRIS,
                    "lineHeight": "1.35",
                    "margin": "4px 0 0",
                },
            )
        )
    return html.Section(hijos, style={"marginBottom": "16px"})


def _maximos_presas(tiempos, presas, xeq):
    """Maximos interiores de presas y periodos pico-a-pico observados.

    No se cuentan los extremos del intervalo como maximos locales.
    Una prominencia minima evita interpretar ruido numerico como ciclos.
    """
    from scipy.signal import find_peaks

    rango = float(np.ptp(presas))
    escala = max(float(np.max(np.abs(presas))), 1.0)
    prominencia = max(0.01 * rango, 0.0001 * escala, 1e-7)
    indices, _ = find_peaks(presas, prominence=prominencia)
    tiempos_max = []
    valores_max = []

    # Ajuste parabolico local: mejor precision que el paso de la malla.
    for i in indices:
        if 0 < i < len(presas) - 1:
            t_3 = tiempos[i - 1 : i + 2]
            x_3 = presas[i - 1 : i + 2]
            coef = np.polyfit(t_3 - tiempos[i], x_3, 2)
            if coef[0] < 0:
                dt = -coef[1] / (2.0 * coef[0])
                dt = float(np.clip(dt, t_3[0] - tiempos[i], t_3[2] - tiempos[i]))
                tiempos_max.append(float(tiempos[i] + dt))
                valores_max.append(float(np.polyval(coef, dt)))
                continue
        tiempos_max.append(float(tiempos[i]))
        valores_max.append(float(presas[i]))

    n = len(tiempos_max)
    periodo = (tiempos_max[-1] - tiempos_max[0]) / (n - 1) if n >= 2 else None
    amplitud_inicial = abs(valores_max[0] - xeq) if n else None
    amplitud_final = abs(valores_max[-1] - xeq) if n else None
    cambio_amplitud = (
        100.0 * (1.0 - amplitud_final / amplitud_inicial)
        if n >= 2 and amplitud_inicial > 1e-8
        else None
    )
    return {
        "maximos": n,
        "ciclos": max(n - 1, 0),
        "periodo": periodo,
        "reduccion_amplitud": cambio_amplitud,
        "tiempos_maximos": tiempos_max,
        "valores_maximos": valores_max,
    }


def _extremos_y_desfase(tiempos, presas, depredadores):
    """Cuenta extremos interiores y estima retraso entre picos de poblaciones.

    El criterio de prominencia coincide con el utilizado en el análisis de
    máximos de presas; los resultados son estimaciones de la malla numérica.
    """
    from scipy.signal import find_peaks

    def detectar(valores, signo):
        rango = float(np.ptp(valores))
        escala = max(float(np.max(np.abs(valores))), 1.0)
        prominencia = max(0.01 * rango, 0.0001 * escala, 1e-7)
        indices, _ = find_peaks(signo * valores, prominence=prominencia)
        return tiempos[indices]

    max_presas = detectar(presas, 1)
    min_presas = detectar(presas, -1)
    max_depredadores = detectar(depredadores, 1)
    min_depredadores = detectar(depredadores, -1)

    # Emparejar un maximo de depredadores posterior al de presas dentro del
    # intervalo que termina en el siguiente maximo de presas.
    desfases = []
    pares_desfase = []
    for inicio, fin in zip(max_presas[:-1], max_presas[1:]):
        candidatos = max_depredadores[
            (max_depredadores > inicio) & (max_depredadores < fin)
        ]
        if len(candidatos):
            desfases.append(float(candidatos[0] - inicio))
            pares_desfase.append((float(inicio), float(candidatos[0])))

    return {
        "max_presas": len(max_presas),
        "min_presas": len(min_presas),
        "max_depredadores": len(max_depredadores),
        "min_depredadores": len(min_depredadores),
        "desfase_medio": float(np.mean(desfases)) if desfases else None,
        "desfases_emparejados": len(desfases),
        "tiempos_maximos_depredadores": max_depredadores.tolist(),
        "pares_desfase": pares_desfase,
    }


def _seccion_extremos_desfase(datos_extremos):
    """Diagnostico opcional, sin ocupar espacio hasta que se despliega."""
    desfase = datos_extremos["desfase_medio"]
    parejas = datos_extremos["desfases_emparejados"]
    return html.Div(
        [
            html.Div(
                _titulo_completo("Extremos y desfase entre poblaciones"),
            ),
            _cuadricula_metricas(
                [
                    ("Máximos de presas", str(datos_extremos["max_presas"])),
                    ("Mínimos de presas", str(datos_extremos["min_presas"])),
                    (
                        "Máximos de depredadores",
                        str(datos_extremos["max_depredadores"]),
                    ),
                    (
                        "Mínimos de depredadores",
                        str(datos_extremos["min_depredadores"]),
                    ),
                    (
                        "Retraso medio: depredadores tras presas",
                        f"{desfase:.2f}" if desfase is not None else "No estimable",
                    ),
                ],
                minimo=210,
            ),
            html.P(
                "Se compara el primer máximo de depredadores posterior a cada "
                "máximo de presas y anterior al máximo siguiente de presas. "
                f"Pares comparables: {parejas}. Son estimaciones de la solución "
                "numérica; si no hay picos suficientes, el desfase no se estima.",
                style={
                    "fontSize": "12px",
                    "lineHeight": "1.45",
                    "color": GRIS,
                    "margin": "9px 0 0",
                },
            ),
        ],
        style={
            "marginBottom": "18px",
        },
    )


def _titulo_completo(titulo):
    """Encabezado compartido para las secciones de Simulacion completa."""
    return html.H3(
        titulo,
        style={
            "fontSize": "16px",
            "fontWeight": 750,
            "color": AZUL,
            "borderBottom": f"1px solid {BORDE}",
            "paddingBottom": "7px",
            "margin": "0 0 11px",
        },
    )


def _cuadricula_metricas(metricas, minimo=190):
    """Tarjetas con columnas que se adaptan al ancho disponible."""
    return html.Div(
        [_metrica(titulo, valor) for titulo, valor in metricas],
        style={
            "display": "grid",
            "gridTemplateColumns": f"repeat(auto-fit, minmax(min(100%, {minimo}px), 1fr))",
            "gap": "12px",
            "minWidth": 0,
        },
    )


def _resultado_con_formula(etiqueta, valor, formula):
    """Un resultado calculado y su formula, asociados en la misma tarjeta."""
    texto = str(etiqueta).lower()
    color_valor = (
        PRESAS
        if "presas" in texto
        else DEPREDADORES
        if "depredadores" in texto
        else AZUL
    )
    return html.Div(
        [
            html.Div(
                etiqueta,
                className="lv-calculo-etiqueta",
                style={"color": color_valor if color_valor != AZUL else GRIS},
            ),
            html.Div(
                str(valor),
                className="lv-calculo-valor",
                style={"color": color_valor},
            ),
            html.Div(_math(formula), className="lv-calculo-formula"),
        ],
        className="lv-calculo-paso",
    )


def _seccion_con_calculos(titulo, calculos, nota=None):
    """Orden de lectura: resultado y formula de cada magnitud."""
    return html.Section(
        [
            _titulo_completo(titulo),
            html.Div(
                [
                    _resultado_con_formula(etiqueta, valor, formula)
                    for etiqueta, valor, formula in calculos
                ],
                className="lv-calculos-cuadricula",
            ),
            html.P(nota, className="lv-calculos-nota") if nota else None,
        ],
        className="lv-seccion-calculos",
    )


def _panel_formulas_completo(titulo, formulas, nota=None):
    """Formulas agrupadas en un bloque legible, sin alterar sus expresiones."""
    return html.Div(
        [
            html.Div(
                titulo,
                style={
                    "color": AZUL,
                    "fontWeight": 700,
                    "fontSize": "13px",
                    "marginBottom": "7px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                etiqueta, style={"fontSize": "12px", "color": GRIS}
                            ),
                            _math(formula),
                        ],
                        style={"minWidth": 0, "overflow": "visible"},
                    )
                    for etiqueta, formula in formulas
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 265px), 1fr))",
                    "gap": "12px",
                    "alignItems": "start",
                    "minWidth": 0,
                },
            ),
            html.Div(
                nota,
                style={
                    "fontSize": "12px",
                    "color": GRIS,
                    "lineHeight": "1.5",
                    "marginTop": "4px",
                },
            )
            if nota
            else None,
        ],
        className="lv-formulas-completo",
        style={
            "borderTop": f"1px solid {BORDE}",
            "padding": "10px 0 2px",
            "marginTop": "12px",
        },
    )


def _seccion_ciclos_clasico(n_maximos, n_ciclos, periodo):
    """Tres indicadores y formulas del periodo en un desplegable."""
    return html.Section(
        [
            _titulo_completo("Ciclos y período observado"),
            _cuadricula_metricas(
                [
                    ("Máximos locales de presas", str(n_maximos)),
                    ("Ciclos pico a pico", str(n_ciclos)),
                    (
                        "Período medio observado",
                        f"{periodo:.2f}" if periodo is not None else "No estimable",
                    ),
                ],
                minimo=215,
            ),
            html.Div(
                [
                    _panel_formulas_completo(
                        "Fórmulas del período observado",
                        [
                            ("Tiempo entre máximos consecutivos", r"T_i=t_{i+1}-t_i"),
                            (
                                "Período medio observado",
                                r"\widehat T=\frac{t_n-t_1}{n-1}",
                            ),
                        ],
                        nota=(
                            "t_i es el instante del máximo de presas número i; "
                            "T_i es el tiempo hasta el máximo siguiente. "
                            "Se necesitan al menos dos máximos para estimar el período medio."
                        ),
                    ),
                ],
                style={"marginTop": "10px"},
            ),
        ],
        style={"marginBottom": "22px", "minWidth": 0},
    )


def _seccion_referencia_clasico(t_lineal, duracion, periodo):
    """Referencia local con sus formulas originales disponibles desplegando."""
    return html.Section(
        [
            _titulo_completo("Referencia cerca del equilibrio"),
            _cuadricula_metricas(
                [
                    ("Período lineal aproximado", f"{t_lineal:.2f}"),
                    (
                        "Ciclos equivalentes en el intervalo",
                        f"{duracion / periodo:.2f}"
                        if periodo is not None and periodo > 0
                        else "No estimable",
                    ),
                ],
                minimo=260,
            ),
            html.Div(
                "El período lineal es una referencia teórica cerca del equilibrio. "
                "Los ciclos equivalentes se calculan con el período medio observado; "
                "ambos valores pueden diferir.",
                style={
                    "fontSize": "12px",
                    "color": GRIS,
                    "lineHeight": "1.5",
                    "marginTop": "10px",
                },
            ),
            html.Div(
                [
                    _panel_formulas_completo(
                        "Fórmulas de referencia",
                        [
                            (
                                "Período lineal aproximado",
                                r"T_{\mathrm{lin}}=\frac{2\pi}{\sqrt{\alpha\gamma}}",
                            ),
                            (
                                "Ciclos equivalentes",
                                r"N_{\mathrm{equiv}}\approx\frac{t_f-t_0}{\widehat T}",
                            ),
                        ],
                    ),
                ],
                style={"marginTop": "2px"},
            ),
        ],
        style={"marginBottom": "22px", "minWidth": 0},
    )


def _interpretacion_global_clasico(n_maximos, n_ciclos, periodo, t_lineal):
    """Interpreta indicadores existentes sin hacer calculos nuevos del modelo."""
    if periodo is not None and periodo > 0:
        diferencia = abs(periodo - t_lineal) / t_lineal * 100.0
        texto = (
            f"En el intervalo analizado se identificaron {n_maximos} máximos locales "
            f"de presas, correspondientes a {n_ciclos} intervalos pico a pico. "
            f"El período medio observado es {periodo:.2f}, frente al período "
            f"lineal aproximado de {t_lineal:.2f}. La diferencia relativa "
            f"respecto de la referencia lineal es {diferencia:.1f} %. "
            "El modelo clásico admite órbitas periódicas; el período lineal "
            "es una aproximación válida cerca del equilibrio."
        )
    elif n_maximos == 1:
        texto = (
            "Se detectó un solo máximo local de presas en el intervalo. "
            "No hay dos máximos consecutivos para estimar un período observado. "
            f"El período lineal teórico cerca del equilibrio es {t_lineal:.2f}."
        )
    else:
        texto = (
            "No se detectaron máximos locales de presas suficientes para "
            "estimar un período observado en este intervalo. "
            f"La referencia lineal cerca del equilibrio es {t_lineal:.2f}."
        )

    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        style={
                            "width": "4px",
                            "backgroundColor": "#2563eb",
                            "borderRadius": "4px",
                            "flexShrink": 0,
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                "Interpretación global",
                                style={
                                    "fontSize": "16px",
                                    "fontWeight": 750,
                                    "color": AZUL,
                                    "marginBottom": "8px",
                                },
                            ),
                            html.Div(
                                texto,
                                style={
                                    "fontSize": "13px",
                                    "fontWeight": 400,
                                    "lineHeight": "1.6",
                                    "color": AZUL,
                                },
                            ),
                        ],
                        style={"minWidth": 0},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "stretch",
                    "gap": "14px",
                    "border": "1px solid #DFE5EC",
                    "backgroundColor": "#F3F5F7",
                    "borderRadius": "12px",
                    "padding": "15px 16px",
                },
            ),
        ],
        style={"marginBottom": "4px", "minWidth": 0},
    )


def _seccion_logistica(titulo, metricas, formulas=None, nota=None, minimo=215):
    """Tarjetas uniformes y formulas opcionales en un desplegable."""
    hijos = [
        _titulo_completo(titulo),
        _cuadricula_metricas(metricas, minimo=minimo),
    ]
    if nota:
        hijos.append(
            html.Div(
                nota,
                style={
                    "fontSize": "12px",
                    "color": GRIS,
                    "lineHeight": "1.5",
                    "marginTop": "10px",
                },
            )
        )
    if formulas:
        hijos.append(
            html.Div(
                [
                    _panel_formulas_completo(
                        "Fórmulas de referencia",
                        formulas,
                    ),
                ],
                style={"marginTop": "8px"},
            )
        )
    return html.Section(
        hijos,
        style={"marginBottom": "22px", "minWidth": 0},
    )


def _interpretacion_global_logistica(texto):
    """La misma tarjeta de interpretacion que en el modelo clasico."""

    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        style={
                            "width": "4px",
                            "backgroundColor": "#2563eb",
                            "borderRadius": "4px",
                            "flexShrink": 0,
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                "Interpretación global",
                                style={
                                    "fontSize": "16px",
                                    "fontWeight": 750,
                                    "color": AZUL,
                                    "marginBottom": "8px",
                                },
                            ),
                            html.Div(
                                texto,
                                style={
                                    "fontSize": "13px",
                                    "fontWeight": 400,
                                    "lineHeight": "1.6",
                                    "color": AZUL,
                                },
                            ),
                        ],
                        style={"minWidth": 0},
                    ),
                ],
                style={
                    "display": "flex",
                    "alignItems": "stretch",
                    "gap": "14px",
                    "border": "1px solid #DFE5EC",
                    "backgroundColor": "#F3F5F7",
                    "borderRadius": "12px",
                    "padding": "15px 16px",
                },
            ),
        ],
        style={"marginBottom": "4px", "minWidth": 0},
    )


def _rangos_mini_fase(presas, depredadores, xeq, yeq):
    """Ventana estable del mini plano; la activacion no mueve la trayectoria."""
    x = np.asarray(presas, dtype=float)
    y = np.asarray(depredadores, dtype=float)
    menor_x = min(float(np.min(x)), float(xeq))
    mayor_x = max(float(np.max(x)), float(xeq))
    menor_y = min(float(np.min(y)), float(yeq))
    mayor_y = max(float(np.max(y)), float(yeq))

    # Un equilibrio constante necesita una ventana visible alrededor del punto.
    ancho_x = max(mayor_x - menor_x, 0.08 * max(mayor_x, 1.0), 1.0)
    ancho_y = max(mayor_y - menor_y, 0.08 * max(mayor_y, 1.0), 1.0)
    margen_x = 0.10 * ancho_x
    margen_y = 0.12 * ancho_y
    return (
        (max(0.0, menor_x - margen_x), mayor_x + margen_x),
        (max(0.0, menor_y - margen_y), mayor_y + margen_y),
    )


def _agregar_nulclinas_mini_fase(
    figura, modelo, alpha, beta, gamma, delta, k, rango_x, rango_y
):
    """Dos ramas interiores de las nulclinas; ocultas por defecto.

    En x=0 tambien se anula x', y en y=0 se anula y'. Estos ejes
    se explican en el detalle matematico; no se superponen como trazas.
    """
    xmin, xmax = rango_x
    ymin, ymax = rango_y
    x0 = max(0.0, xmin)

    # Nulclina de presas en el interior: horizontal en el clasico;
    # decreciente para el logistico (solo la porcion biologica y >= 0).
    if modelo == "logistico":
        extremo = min(xmax, float(k))
        xx = np.linspace(x0, extremo, 60) if extremo > x0 else np.array([])
        yy = (alpha / beta) * (1.0 - xx / k) if xx.size else np.array([])
    else:
        xx = np.array([x0, xmax])
        yy = np.array([alpha / beta, alpha / beta])

    figura.add_trace(
        go.Scatter(
            x=xx,
            y=yy,
            mode="lines",
            visible=False,
            name="Nulclina de presas: x′ = 0",
            meta="nulclina",
            line={"color": PRESAS, "width": 1.6, "dash": "dot"},
            hovertemplate="Nulclina x′ = 0<br>x=%{x:.2f} · y=%{y:.2f}<extra></extra>",
            showlegend=False,
        )
    )

    # Nulclina de depredadores en el interior: x = gamma / delta.
    x_vertical = float(gamma / delta)
    figura.add_trace(
        go.Scatter(
            x=[x_vertical, x_vertical],
            y=[ymin, ymax],
            mode="lines",
            visible=False,
            name="Nulclina de depredadores: y′ = 0",
            meta="nulclina",
            line={"color": DEPREDADORES, "width": 1.6, "dash": "dot"},
            hovertemplate="Nulclina y′ = 0<br>x=%{x:.2f}<extra></extra>",
            showlegend=False,
        )
    )

    # Las líneas se controlan desde un interruptor Dash fuera de Plotly.


def _explicacion_nulclinas(modelo, alpha, beta, gamma, delta, k, coexistencia):
    """Fundamento y signos en la pestana de equilibrio, sin recargar la vista."""
    if modelo == "logistico":
        nulclina_presas = r"y=\frac{\alpha}{\beta}\left(1-\frac{x}{K}\right)"
        nota = (
            "La recta de presas es descendente y su rama positiva termina "
            "en x = K. "
            + (
                "Las nulclinas interiores se cortan en el equilibrio de coexistencia."
                if coexistencia
                else "No hay cruce de nulclinas en el interior positivo: K no supera γ/δ."
            )
        )
    else:
        nulclina_presas = r"y=\frac{\alpha}{\beta}"
        nota = "Las dos rectas interiores se cortan en el equilibrio de coexistencia."

    umbral_presas = alpha / beta
    umbral_depredadores = gamma / delta
    texto = (
        "Las nulclinas son los lugares donde una derivada se hace cero. "
        "En el primer cuadrante, las ramas interiores son:\n\n"
        f"- Presas: ${nulclina_presas}$.\n"
        r"- Depredadores: $x=\frac{\gamma}{\delta}$."
        "\n\n"
        "**Signos para x > 0, y > 0:** por debajo de la nulclina "
        "de presas, x′ > 0; por encima, x′ < 0. "
        "A la derecha de x = γ/δ, y′ > 0; a la izquierda, y′ < 0. "
        "Sobre cada nulclina, la derivada correspondiente es cero.\n\n"
        "Los ejes x = 0 y y = 0 también son ramas de nulclinas, "
        "pero no se destacan en el dibujo. " + nota + "\n\n"
        f"**Con estos parámetros:** α/β = {umbral_presas:.2f} y "
        f"γ/δ = {umbral_depredadores:.2f}."
    )
    return html.Details(
        [
            html.Summary("¿Qué indican las nulclinas y los signos de las derivadas?"),
            dcc.Markdown(
                texto,
                mathjax=True,
                style={
                    "padding": "8px 2px 2px",
                    "fontSize": "12px",
                    "lineHeight": "1.5",
                    "color": "#454545",
                },
            ),
            html.P(
                "Línea turquesa: x′ = 0; línea violeta: y′ = 0. "
                "Activa «Mostrar nulclinas» sobre el miniplano para verlas.",
                style={"fontSize": "11px", "color": GRIS, "margin": "2px 0 0"},
            ),
        ],
        className="lv-interpretacion-detallada",
    )


def _grafico_fases_diagnostico(
    presas, depredadores, xeq, yeq, modelo, alpha, beta, gamma, delta, k
):
    """Miniplano simulado con flecha temporal y nulclinas opcionales."""
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=presas,
            y=depredadores,
            line={"color": "#37678F", "width": 2.2},
            **estilo_flechas_fase(
                presas, depredadores, cantidad=1, tamano=9, color="#37678F"
            ),
            name="Trayectoria simulada",
            hovertemplate="Presas: %{x:.2f}<br>Depredadores: %{y:.2f}<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=[float(presas[0])],
            y=[float(depredadores[0])],
            mode="markers",
            marker={"color": "#315E8D", "size": 8, "symbol": "circle"},
            name="Inicio",
            hovertemplate="Inicio: (%{x:.2f}, %{y:.2f})<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=[float(presas[-1])],
            y=[float(depredadores[-1])],
            mode="markers",
            marker={"color": "#8B3158", "size": 8, "symbol": "diamond"},
            name="Final",
            hovertemplate="Final: (%{x:.2f}, %{y:.2f})<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=[xeq],
            y=[yeq],
            mode="markers",
            marker={
                "color": "#0B2345",
                "size": 10,
                "symbol": "x",
                "line": {"width": 2},
            },
            name="Equilibrio",
            hovertemplate="Equilibrio: (%{x:.2f}, %{y:.2f})<extra></extra>",
        )
    )

    rango_x, rango_y = _rangos_mini_fase(presas, depredadores, xeq, yeq)
    _agregar_nulclinas_mini_fase(
        figura, modelo, alpha, beta, gamma, delta, k, rango_x, rango_y
    )
    figura.update_layout(
        height=180,
        margin={"l": 30, "r": 8, "t": 10, "b": 26},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font={"family": "inherit", "size": 9, "color": "#52677E"},
        hovermode="closest",
        dragmode=False,
    )
    figura.update_xaxes(
        title_text="Presas",
        title_font={"size": 9},
        tickfont={"size": 8},
        range=list(rango_x),
        fixedrange=True,
        zeroline=False,
        showgrid=False,
    )
    figura.update_yaxes(
        title_text="Depred.",
        title_font={"size": 9},
        tickfont={"size": 8},
        range=list(rango_y),
        fixedrange=True,
        zeroline=False,
        showgrid=False,
    )
    return dcc.Graph(
        figure=figura,
        config={"displayModeBar": False, "responsive": True},
        className="lv-grafico-fases-resumen",
        style={"height": "180px", "width": "100%"},
        id="lv-nulclinas-miniplano",
    )


def _grafico_eventos_completo(tiempos, presas, depredadores, maximos, extremos):
    """Curvas reales; los marcadores usan los mismos detectores de picos."""
    figura = go.Figure()
    figura.add_trace(
        go.Scatter(
            x=tiempos,
            y=presas,
            mode="lines",
            name="Presas",
            line={"color": PRESAS, "width": 2.6},
            hovertemplate="t = %{x:.2f}<br>Presas = %{y:.2f}<extra></extra>",
        )
    )
    figura.add_trace(
        go.Scatter(
            x=tiempos,
            y=depredadores,
            mode="lines",
            name="Depredadores",
            line={"color": DEPREDADORES, "width": 2.4},
            hovertemplate="t = %{x:.2f}<br>Depredadores = %{y:.2f}<extra></extra>",
        )
    )
    t_picos = maximos["tiempos_maximos"]
    if t_picos:
        figura.add_trace(
            go.Scatter(
                x=t_picos,
                y=maximos["valores_maximos"],
                mode="markers",
                marker={
                    "color": PRESAS,
                    "size": 9,
                    "symbol": "circle",
                    "line": {"color": "#FFFFFF", "width": 1.5},
                },
                name="Máximos de presas",
                hovertemplate="Máximo de presas<br>t = %{x:.2f}<br>Valor = %{y:.2f}<extra></extra>",
            )
        )
    t_depredadores = extremos["tiempos_maximos_depredadores"]
    if t_depredadores:
        figura.add_trace(
            go.Scatter(
                x=t_depredadores,
                y=np.interp(t_depredadores, tiempos, depredadores),
                mode="markers",
                marker={"color": DEPREDADORES, "size": 8, "symbol": "diamond"},
                name="Máximos de depredadores",
                hovertemplate="Máximo de depredadores<br>t = %{x:.2f}<br>Valor = %{y:.2f}<extra></extra>",
            )
        )
    pares = extremos["pares_desfase"]
    if pares:
        # Solo el primer par se marca; no confundirlo con el promedio de todos los pares.
        inicio, fin = pares[0]
        maximo_global = max(float(np.max(presas)), float(np.max(depredadores)))
        minimo_global = min(float(np.min(presas)), float(np.min(depredadores)))
        nivel = minimo_global + 0.88 * (maximo_global - minimo_global)
        figura.add_trace(
            go.Scatter(
                x=[inicio, fin],
                y=[nivel, nivel],
                mode="lines+markers",
                line={"color": "#315E8D", "width": 2, "dash": "dot"},
                marker={"size": 6, "color": "#315E8D"},
                showlegend=False,
                hovertemplate="Par de picos: t = %{x:.2f}<extra></extra>",
            )
        )
        figura.add_annotation(
            x=(inicio + fin) / 2.0,
            y=nivel,
            text=f"Δt primer par = {fin - inicio:.2f}",
            showarrow=False,
            yshift=14,
            font={"size": 10, "color": "#315E8D"},
            bgcolor="#FFFFFF",
            bordercolor="#DFE7F0",
            borderpad=3,
        )
    figura.update_layout(
        height=300,
        margin={"l": 46, "r": 16, "t": 12, "b": 42},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={"family": "inherit", "size": 11, "color": "#52677E"},
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.16, "x": 0},
    )
    figura.update_xaxes(
        title_text="Tiempo",
        gridcolor="#EBEEF2",
        zeroline=False,
        range=[float(tiempos[0]), float(tiempos[-1])],
    )
    figura.update_yaxes(title_text="Poblaciones", gridcolor="#EBEEF2", zeroline=False)
    return html.Section(
        [
            html.H3(
                "Trayectorias y máximos detectados",
                className="lv-grafico-eventos-titulo",
            ),
            dcc.Graph(
                figure=figura,
                config={"displayModeBar": False, "responsive": True},
                style={"height": "300px", "width": "100%"},
            ),
            html.P(
                "Los puntos señalan máximos detectados numéricamente. "
                "El segmento punteado, cuando aparece, corresponde al primer par "
                "de máximos comparable; el retraso medio considera todos los pares válidos.",
                className="lv-grafico-eventos-nota",
            ),
        ],
        className="lv-grafico-eventos-panel",
    )


def _tarjeta_diagnostico_escenario(
    tipo, movimiento, explicacion, variante, autovalores, grafico
):
    """Diagnostico compacto con mini trayectoria real y autovalores calculados."""
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        "Plano de fases · trayectoria simulada",
                        className="lv-fase-mini-etiqueta",
                    ),
                    html.Div(
                        dbc.Switch(
                            id="lv-nulclinas-interruptor",
                            label="Mostrar nulclinas",
                            value=False,
                            class_name="lv-nulclinas-switch",
                        ),
                        className="lv-nulclinas-control",
                    ),
                    grafico,
                    html.Div(
                        "● Inicio    ◆ Final    × Equilibrio",
                        className="lv-fase-mini-leyenda",
                    ),
                ],
                className="lv-diagnostico-visual",
            ),
            html.Div(
                [
                    html.Div(
                        "DIAGNÓSTICO DEL ESCENARIO", className="lv-diagnostico-etiqueta"
                    ),
                    html.H3(tipo, className="lv-diagnostico-resultado"),
                    html.Div(movimiento, className="lv-diagnostico-movimiento"),
                    html.P(explicacion, className="lv-diagnostico-explicacion"),
                    html.Div(
                        [html.Strong("Autovalores · "), html.Span(autovalores)],
                        className="lv-diagnostico-chip",
                    ),
                    html.P(
                        "Clasificación local calculada con los parámetros actuales.",
                        className="lv-diagnostico-aviso",
                    ),
                ],
                className="lv-diagnostico-informacion",
            ),
        ],
        className=f"lv-diagnostico-escenario lv-diagnostico-{variante}",
    )


def _trayectoria_constante_en_equilibrio(presas, depredadores, xeq, yeq):
    """Indica si toda la solucion coincide numericamente con el equilibrio.

    No basta con una distancia final pequena: se comprueba toda la trayectoria.
    La tolerancia relativa admite unicamente errores numericos minimos.
    """
    x = np.asarray(presas, dtype=float)
    y = np.asarray(depredadores, dtype=float)
    if not x.size or x.shape != y.shape:
        return False
    if not (np.all(np.isfinite(x)) and np.all(np.isfinite(y))):
        return False
    if not (np.isfinite(xeq) and np.isfinite(yeq)):
        return False

    tolerancia_x = 1e-7 * max(1.0, abs(float(xeq)), float(np.max(np.abs(x))))
    tolerancia_y = 1e-7 * max(1.0, abs(float(yeq)), float(np.max(np.abs(y))))
    return bool(
        np.all(np.abs(x - float(xeq)) <= tolerancia_x)
        and np.all(np.abs(y - float(yeq)) <= tolerancia_y)
    )


def _lectura_rapida_completa(
    diagnostico,
    n_maximos,
    n_ciclos,
    periodo,
    distancia_inicial,
    distancia_final,
    trayectoria_constante=False,
):
    tipo = diagnostico[0].lower()
    if trayectoria_constante:
        nota_lineal = (
            " La escala lineal de oscilación describe pequeñas perturbaciones "
            "del equilibrio, no un período observado en esta simulación."
            if diagnostico[3] in ("centro", "foco")
            else ""
        )
        return html.Div(
            [
                html.Strong("Lectura rápida · "),
                html.Span(
                    "Las poblaciones permanecen constantes en el equilibrio: "
                    "no se observan oscilaciones ni extremos locales. "
                    "La clasificación matemática caracteriza el comportamiento "
                    "de trayectorias cercanas." + nota_lineal
                ),
            ],
            className="lv-lectura-rapida",
        )
    if periodo is None:
        resumen_picos = (
            f"Se identificaron {n_maximos} máximos de presas y {n_ciclos} "
            "intervalos pico a pico; no hay suficientes máximos para estimar "
            "una separación media."
        )
    else:
        resumen_picos = (
            f"Se identificaron {n_maximos} máximos de presas y {n_ciclos} "
            f"intervalos pico a pico (separación media: {periodo:.2f})."
        )
    if distancia_inicial is None or distancia_final is None:
        resumen_distancia = "La distancia relativa al equilibrio no está definida."
    else:
        resumen_distancia = (
            f"La distancia al equilibrio pasó de {distancia_inicial:.1f}% "
            f"a {distancia_final:.1f}% en el intervalo."
        )
    return html.Div(
        [
            html.Strong("Lectura rápida · "),
            html.Span(
                f"Diagnóstico local: {tipo}. {resumen_picos} {resumen_distancia}"
            ),
        ],
        className="lv-lectura-rapida",
    )


def _detalle_interpretacion_completa(contenido):
    """Conserva el texto desarrollado sin repetirlo en el resumen fijo."""
    return html.Details(
        [
            html.Summary("Ver interpretación matemática detallada"),
            contenido,
        ],
        className="lv-interpretacion-detallada",
    )


def _vista_completa(
    modelo,
    tiempos,
    presas,
    depredadores,
    xeq,
    yeq,
    coexistencia,
    alpha,
    beta,
    gamma,
    delta,
    k,
):
    """Diagnostico de toda la trayectoria; distingue ciclos y transitorios."""
    x0, y0 = float(presas[0]), float(depredadores[0])
    xf, yf = float(presas[-1]), float(depredadores[-1])
    duracion = float(tiempos[-1] - tiempos[0])
    variacion_x = 100.0 * (xf / x0 - 1.0) if x0 else None
    variacion_y = 100.0 * (yf / y0 - 1.0) if y0 else None
    distancia_inicial = _distancia_relativa(x0, y0, xeq, yeq)
    distancia_final = _distancia_relativa(xf, yf, xeq, yeq)
    trayectoria_constante = _trayectoria_constante_en_equilibrio(
        presas, depredadores, xeq, yeq
    )

    resultado_maximos = _maximos_presas(tiempos, presas, xeq)
    periodo = resultado_maximos["periodo"]
    n_maximos = resultado_maximos["maximos"]
    n_ciclos = resultado_maximos["ciclos"]

    secciones_equilibrio = [
        _seccion_con_calculos(
            "Equilibrio de coexistencia"
            if coexistencia
            else "Equilibrio sin depredadores",
            [
                (
                    "Presas x*",
                    f"{xeq:.2f}",
                    r"x^*=\frac{\gamma}{\delta}" if coexistencia else r"x^*=K",
                ),
                (
                    "Depredadores y*",
                    f"{yeq:.2f}",
                    (
                        r"y^*=\frac{\alpha}{\beta}"
                        if modelo == "clasico"
                        else r"y^*=\frac{\alpha}{\beta}\left(1-\frac{x^*}{K}\right)"
                    )
                    if coexistencia
                    else r"y^*=0",
                ),
            ],
            nota="Equilibrio de referencia: ambas derivadas de población son nulas.",
        ),
    ]
    secciones_oscilaciones = []
    secciones_evolucion = []
    texto_autovalores = ""
    referencia_lineal = None

    if modelo == "clasico":
        diagnostico = (
            "Centro",
            "Órbitas cerradas alrededor del equilibrio",
            "El equilibrio de coexistencia es un centro: las órbitas cercanas "
            "son periódicas y no convergen hacia él.",
            "centro",
        )
        omega_clasico = np.sqrt(alpha * gamma)
        t_lineal = 2.0 * np.pi / omega_clasico
        texto_autovalores = f"± {omega_clasico:.4f}i"
        referencia_lineal = t_lineal
        secciones_equilibrio.append(
            _seccion_con_calculos(
                "Autovalores del jacobiano · Centro",
                [
                    ("Traza del jacobiano", "0.0000", r"\operatorname{tr}(J_*)=0"),
                    (
                        "Determinante del jacobiano",
                        f"{alpha * gamma:.4f}",
                        r"\det(J_*)=\alpha\gamma",
                    ),
                    (
                        "Frecuencia angular local",
                        f"{omega_clasico:.4f}",
                        r"\omega=\sqrt{\det(J_*)}=\sqrt{\alpha\gamma}",
                    ),
                    (
                        "Autovalores",
                        f"± {omega_clasico:.4f}i",
                        r"\lambda_{1,2}=\pm i\omega",
                    ),
                ],
                nota=(
                    "Los autovalores son imaginarios puros. En este modelo clásico "
                    "las trayectorias alrededor del equilibrio son órbitas cerradas."
                ),
            )
        )
        secciones_oscilaciones.append(
            _seccion_ciclos_clasico(n_maximos, n_ciclos, periodo)
        )
        secciones_oscilaciones.append(
            _seccion_referencia_clasico(t_lineal, duracion, periodo)
        )

    elif coexistencia:
        # Se conservan exactamente las formulas y la clasificacion original.
        traza = -alpha * xeq / k
        determinante = alpha * gamma * (1.0 - xeq / k)
        discriminante = traza**2 - 4.0 * determinante
        tolerancia = 1e-9 * max(1.0, abs(traza**2), abs(4.0 * determinante))

        if discriminante < -tolerancia:
            diagnostico = (
                "Foco estable",
                "Espiral amortiguada",
                "Cerca del equilibrio de coexistencia, la trayectoria gira "
                "y su amplitud disminuye progresivamente.",
                "foco",
            )
            omega = np.sqrt(determinante - traza**2 / 4.0)
            t_lineal = 2.0 * np.pi / omega
            tau = -2.0 / traza

            texto_autovalores = f"{traza / 2:+.4f} ± {omega:.4f}i"
            referencia_lineal = t_lineal
            secciones_oscilaciones.append(
                _seccion_logistica(
                    "Comportamiento local · Foco estable",
                    [
                        ("Máximos de presas", str(n_maximos)),
                        ("Intervalos pico a pico", str(n_ciclos)),
                        (
                            "Separación media observada",
                            f"{periodo:.2f}" if periodo is not None else "No estimable",
                        ),
                    ],
                    formulas=[
                        ("Tiempo entre máximos consecutivos", r"T_i=t_{i+1}-t_i"),
                        (
                            "Separación media observada",
                            r"\widehat T=\frac{t_n-t_1}{n-1}",
                        ),
                    ],
                    nota=(
                        "Los máximos describen oscilaciones transitorias de una "
                        "espiral amortiguada, no ciclos periódicos permanentes. "
                        "t_i es el instante del máximo de presas número i. "
                        "Se necesitan al menos dos máximos para estimar su separación."
                    ),
                )
            )

            parte_real = traza / 2.0
            secciones_equilibrio.append(
                _seccion_con_calculos(
                    "Autovalores del jacobiano · Foco estable",
                    [
                        (
                            "Traza del jacobiano",
                            f"{traza:+.4f}",
                            r"\operatorname{tr}(J_*)=-\frac{\alpha x^*}{K}",
                        ),
                        (
                            "Determinante del jacobiano",
                            f"{determinante:.4f}",
                            r"\det(J_*)=\alpha\gamma\left(1-\frac{x^*}{K}\right)",
                        ),
                        (
                            "Frecuencia angular local",
                            f"{omega:.4f}",
                            r"\omega=\sqrt{\det(J_*)-\frac{(\operatorname{tr}J_*)^2}{4}}",
                        ),
                        (
                            "Autovalores",
                            f"{parte_real:+.4f} ± {omega:.4f}i",
                            r"\lambda_{1,2}=\frac{\operatorname{tr}(J_*)}{2}\pm i\omega",
                        ),
                    ],
                    nota=(
                        f"D = (tr J*)² − 4 det(J*) = {discriminante:.4f} < 0: autovalores "
                        "complejos conjugados con parte real negativa. "
                        "La clasificación es local."
                    ),
                )
            )

            secciones_oscilaciones.append(
                _seccion_logistica(
                    "Oscilación y amortiguamiento cerca del equilibrio",
                    [
                        ("Escala local de oscilación", f"{t_lineal:.2f}"),
                        ("Tiempo característico de amortiguamiento", f"{tau:.2f}"),
                        (
                            "Reducción entre amplitudes máximas",
                            f"{resultado_maximos['reduccion_amplitud']:.1f}%"
                            if resultado_maximos["reduccion_amplitud"] is not None
                            else "No estimable",
                        ),
                    ],
                    formulas=[
                        (
                            "Período lineal aproximado",
                            r"T_{\mathrm{lin}}=\frac{2\pi}{\omega}",
                        ),
                        (
                            "Escala de amortiguamiento",
                            r"\tau=-\frac{2}{\operatorname{tr}J_*}",
                        ),
                    ],
                    nota=(
                        "Estas son aproximaciones locales. El tiempo τ caracteriza "
                        "la reducción de amplitud por un factor 1/e cerca del "
                        "equilibrio. La reducción observada se calcula a partir "
                        "de |máximo de presas − x*| y puede ser negativa."
                    ),
                )
            )

            if periodo is not None and periodo > 0:
                interpretacion_logistica = (
                    f"El equilibrio de coexistencia es un foco estable. En el "
                    f"intervalo se identificaron {n_maximos} máximos de presas "
                    f"y {n_ciclos} intervalos pico a pico, con separación media "
                    f"observada de {periodo:.2f}. La escala de oscilación lineal "
                    f"cerca del equilibrio es {t_lineal:.2f}. "
                    "Se trata de oscilaciones amortiguadas, no de ciclos "
                    "periódicos permanentes."
                )
            else:
                interpretacion_logistica = (
                    "El equilibrio de coexistencia es un foco estable: las "
                    "soluciones cercanas pueden oscilar mientras se amortiguan. "
                    f"En el intervalo se identificaron {n_maximos} máximos; "
                    "no hay suficientes para estimar una separación media "
                    f"observada. La escala lineal local es {t_lineal:.2f}."
                )
        else:
            diagnostico = (
                "Nodo estable",
                "Convergencia local sin oscilaciones repetidas",
                "Cerca del equilibrio de coexistencia, las trayectorias se "
                "aproximan sin giros repetidos.",
                "nodo",
            )
            raiz = np.sqrt(max(discriminante, 0.0))
            lambda_lenta = (traza + raiz) / 2.0
            lambda_rapida = (traza - raiz) / 2.0
            tiempo_relajacion = -1.0 / lambda_lenta if lambda_lenta < -1e-12 else None
            texto_autovalores = f"{lambda_lenta:.4f} y {lambda_rapida:.4f}"
            secciones_equilibrio.append(
                _seccion_con_calculos(
                    "Autovalores del jacobiano · Nodo estable",
                    [
                        (
                            "Traza del jacobiano",
                            f"{traza:+.4f}",
                            r"\operatorname{tr}(J_*)=-\frac{\alpha x^*}{K}",
                        ),
                        (
                            "Determinante del jacobiano",
                            f"{determinante:.4f}",
                            r"\det(J_*)=\alpha\gamma\left(1-\frac{x^*}{K}\right)",
                        ),
                        (
                            "Discriminante",
                            f"{discriminante:.4f}",
                            r"D=(\operatorname{tr}J_*)^2-4\det(J_*)",
                        ),
                        (
                            "Autovalores",
                            f"{lambda_lenta:.4f} y {lambda_rapida:.4f}",
                            r"\lambda_{1,2}=\frac{\operatorname{tr}(J_*)\pm\sqrt{D}}{2}",
                        ),
                    ],
                    nota=(
                        "El discriminante es no negativo (o casi nulo según la tolerancia) y los autovalores "
                        "son reales negativos: convergencia local sin espirales."
                    ),
                )
            )
            secciones_equilibrio.append(
                _seccion_logistica(
                    "Comportamiento local · Nodo estable",
                    [
                        ("Período de oscilación local", "No corresponde"),
                        ("Autovalor de decaimiento más lento", f"{lambda_lenta:.4f}"),
                        (
                            "Tiempo característico de relajación",
                            f"{tiempo_relajacion:.2f}"
                            if tiempo_relajacion is not None
                            else "No estimable",
                        ),
                    ],
                    formulas=[
                        (
                            "Tiempo de relajación local",
                            r"\tau=-\frac{1}{\lambda_+}",
                        ),
                    ],
                    nota=(
                        "Cerca del equilibrio hay convergencia sin giros repetidos. "
                        "τ es una escala local de relajación, no el tiempo exacto "
                        "en que se alcanza el equilibrio."
                    ),
                )
            )
            interpretacion_logistica = (
                "El equilibrio de coexistencia es un nodo estable. Cerca de él, "
                "la trayectoria se aproxima sin oscilaciones repetidas; por eso "
                "no corresponde estimar un período de oscilación local. "
                + (
                    f"La escala local de relajación es {tiempo_relajacion:.2f}."
                    if tiempo_relajacion is not None
                    else "No se pudo estimar una escala local de relajación."
                )
            )
    else:
        tasa_borde = delta * k - gamma
        diagnostico = (
            "Sin coexistencia positiva",
            "Equilibrio de borde: (K, 0)",
            "Se está en el umbral K = γ/δ; la clasificación local requiere "
            "un análisis adicional."
            if abs(tasa_borde) <= 1e-10
            else "Los depredadores disminuyen cerca del equilibrio sin "
            "depredadores; no existe equilibrio positivo de coexistencia.",
            "borde",
        )
        condicion = "K = γ/δ" if abs(tasa_borde) <= 1e-10 else "K < γ/δ"
        texto_autovalores = f"{-alpha:+.4f} y {tasa_borde:+.4f}"
        secciones_equilibrio.append(
            _seccion_con_calculos(
                "Jacobiano del equilibrio sin depredadores",
                [
                    (
                        "Traza del jacobiano",
                        f"{-alpha + tasa_borde:+.4f}",
                        r"\operatorname{tr}(J_F)=-\alpha+\delta K-\gamma",
                    ),
                    (
                        "Determinante del jacobiano",
                        f"{-alpha * tasa_borde:.4f}",
                        r"\det(J_F)=-\alpha(\delta K-\gamma)",
                    ),
                    (
                        "Autovalores",
                        texto_autovalores,
                        r"\lambda_1=-\alpha,\quad\lambda_2=\delta K-\gamma",
                    ),
                ],
                nota=(
                    "Las expresiones corresponden al equilibrio de borde (K, 0). "
                    "En K = γ/δ hay un autovalor nulo y la linealización no "
                    "determina por sí sola el comportamiento no lineal."
                ),
            )
        )
        secciones_equilibrio.append(
            _seccion_logistica(
                "Sin equilibrio positivo de coexistencia",
                [
                    ("Condición del modelo", condicion),
                    ("Tasa de depredadores cerca de (K, 0)", f"{tasa_borde:+.4f}"),
                    ("Período de coexistencia", "No corresponde"),
                ],
                formulas=[
                    ("Equilibrio sin depredadores", r"E_F=(K,0)"),
                    (
                        "Tasa relativa de depredadores",
                        r"\frac{y'}{y}\approx\delta K-\gamma",
                    ),
                ],
                nota=(
                    "El equilibrio de referencia es (K, 0). En el umbral "
                    "K = γ/δ la tasa lineal se anula y se requiere un análisis "
                    "adicional."
                ),
            )
        )
        if abs(tasa_borde) <= 1e-10:
            interpretacion_logistica = (
                "No existe un equilibrio de coexistencia positivo. Estamos "
                "en el umbral K = γ/δ: la tasa lineal de los depredadores "
                "se anula cerca de (K, 0) y esta aproximación no basta para "
                "clasificar la dinámica."
            )
        else:
            interpretacion_logistica = (
                "No existe un equilibrio positivo de coexistencia. Cerca de "
                "(K, 0), la tasa relativa de depredadores es negativa, por lo "
                "que disminuyen. No corresponde hablar de períodos de "
                "oscilación de coexistencia."
            )

    # Lectura cualitativa opcional, sin cambiar las secciones existentes.
    secciones_equilibrio.insert(
        1,
        _explicacion_nulclinas(modelo, alpha, beta, gamma, delta, k, coexistencia),
    )

    # La clasificacion (Centro, Foco, Nodo...) describe el equilibrio.
    # Si la solucion parte exactamente de el, no recorre ninguna orbita.
    if trayectoria_constante:
        diagnostico = (
            diagnostico[0],
            "Solución constante · sin oscilaciones observadas",
            "Las poblaciones permanecen constantes porque la condición "
            "inicial coincide con el equilibrio. La clasificación describe "
            "trayectorias cercanas, no oscilaciones de esta solución.",
            diagnostico[3],
        )

    # Resultados de los mismos detectores utilizados para las metricas.
    datos_extremos = _extremos_y_desfase(tiempos, presas, depredadores)
    secciones_oscilaciones.insert(
        0,
        _grafico_eventos_completo(
            tiempos,
            presas,
            depredadores,
            resultado_maximos,
            datos_extremos,
        ),
    )
    secciones_oscilaciones.append(_seccion_extremos_desfase(datos_extremos))

    # Los dos indicadores de evolucion mantienen los calculos y formulas.
    def _indicador_adicional(titulo, metricas, formulas, nota=None):
        return html.Section(
            [
                _titulo_completo(titulo),
                _cuadricula_metricas(metricas, minimo=260),
                _panel_formulas_completo("Fórmulas de referencia", formulas, nota=nota),
            ],
            style={"marginBottom": "18px", "minWidth": 0},
        )

    secciones_evolucion.extend(
        [
            html.Div(
                [
                    html.Div(
                        "Distancia relativa al equilibrio · inicio → final",
                        className="lv-completa-distancia-titulo",
                    ),
                    html.Div(
                        [
                            html.Span(
                                f"{distancia_inicial:.1f}%"
                                if distancia_inicial is not None
                                else "No definida",
                            ),
                            html.Span("→", className="lv-completa-distancia-flecha"),
                            html.Span(
                                f"{distancia_final:.1f}%"
                                if distancia_final is not None
                                else "No definida",
                                className="lv-completa-distancia-final",
                            ),
                        ],
                        className="lv-completa-distancia-valores",
                    ),
                    html.Div(
                        _math(_formula_distancia()),
                        className="lv-completa-distancia-formula",
                    ),
                    html.P(
                        "La distancia compara la separación relativa respecto del "
                        "equilibrio al inicio y al final; puede superar el 100%.",
                        className="lv-calculos-nota",
                    ),
                ],
                className="lv-completa-distancia-panel",
            ),
            _indicador_adicional(
                "Variación total respecto del inicio",
                [
                    ("Presas", _texto_porcentaje(variacion_x)),
                    ("Depredadores", _texto_porcentaje(variacion_y)),
                ],
                [
                    (
                        "Variación de presas",
                        r"\Delta_x=\frac{x(t_f)-x_0}{x_0}\cdot100\%",
                    ),
                    (
                        "Variación de depredadores",
                        r"\Delta_y=\frac{y(t_f)-y_0}{y_0}\cdot100\%",
                    ),
                ],
            ),
        ]
    )

    # Explicacion extensa disponible en la seccion a la que corresponde.
    if modelo == "clasico":
        secciones_oscilaciones.append(
            _detalle_interpretacion_completa(
                _interpretacion_global_clasico(n_maximos, n_ciclos, periodo, t_lineal)
            )
        )
    elif coexistencia and diagnostico[3] == "foco":
        secciones_oscilaciones.append(
            _detalle_interpretacion_completa(
                _interpretacion_global_logistica(interpretacion_logistica)
            )
        )
    else:
        secciones_equilibrio.append(
            _detalle_interpretacion_completa(
                _interpretacion_global_logistica(interpretacion_logistica)
            )
        )

    # El diagnostico siempre visible; las secciones detalladas se navegan por pestanas.
    if diagnostico[3] in ("centro", "foco"):
        metricas_resumen = [
            ("Máximos de presas", str(n_maximos)),
            (
                "Separación media observada",
                f"{periodo:.2f}" if periodo is not None else "No estimable",
            ),
            ("Escala lineal", f"{referencia_lineal:.2f}"),
        ]
    else:
        metricas_resumen = [
            (
                "Distancia final",
                f"{distancia_final:.1f}%"
                if distancia_final is not None
                else "No definida",
            ),
            ("Variación total de presas", _texto_porcentaje(variacion_x)),
            ("Variación total de depredadores", _texto_porcentaje(variacion_y)),
        ]

    contenido = [
        html.Div(
            [
                html.Span("Análisis de la trayectoria completa"),
                html.Span(f"t = {tiempos[0]:g} a {tiempos[-1]:g}"),
            ],
            className="lv-completa-rango",
        ),
        _tarjeta_diagnostico_escenario(
            *diagnostico,
            texto_autovalores,
            _grafico_fases_diagnostico(
                presas,
                depredadores,
                xeq,
                yeq,
                modelo,
                alpha,
                beta,
                gamma,
                delta,
                k,
            ),
        ),
        html.Div(
            [_metrica(etiqueta, valor) for etiqueta, valor in metricas_resumen],
            className="lv-completa-resumen-metricas",
        ),
        _lectura_rapida_completa(
            diagnostico,
            n_maximos,
            n_ciclos,
            periodo,
            distancia_inicial,
            distancia_final,
            trayectoria_constante=trayectoria_constante,
        ),
        dcc.Tabs(
            id="lv-completa-secciones",
            value="equilibrio",
            parent_className="lv-completa-pestanas-contenedor",
            className="lv-completa-pestanas",
            children=[
                dcc.Tab(
                    label="Equilibrio y autovalores",
                    value="equilibrio",
                    className="lv-completa-pestana",
                    selected_className="lv-completa-pestana-activa",
                    children=html.Div(
                        secciones_equilibrio, className="lv-completa-panel"
                    ),
                ),
                dcc.Tab(
                    label="Oscilaciones y desfase",
                    value="oscilaciones",
                    className="lv-completa-pestana",
                    selected_className="lv-completa-pestana-activa",
                    children=html.Div(
                        secciones_oscilaciones, className="lv-completa-panel"
                    ),
                ),
                dcc.Tab(
                    label="Evolución y distancia",
                    value="evolucion",
                    className="lv-completa-pestana",
                    selected_className="lv-completa-pestana-activa",
                    children=html.Div(
                        secciones_evolucion, className="lv-completa-panel"
                    ),
                ),
            ],
        ),
    ]
    return html.Div(contenido, className="lv-vista-completa", style={"minWidth": 0})


def registrar_callbacks_analisis_lv(app):
    @app.callback(
        Output("lv-nulclinas-miniplano", "figure"),
        Input("lv-nulclinas-interruptor", "value"),
        State("lv-nulclinas-miniplano", "figure"),
        prevent_initial_call=True,
    )
    def alternar_nulclinas_miniplano(activado, figura):
        """Cambia solo las dos nulclinas; conserva trayectoria y marcadores."""
        if not figura:
            from dash.exceptions import PreventUpdate

            raise PreventUpdate
        for traza in figura.get("data", []):
            if traza.get("meta") == "nulclina":
                traza["visible"] = bool(activado)
        return figura

    @app.callback(
        Output("lv-modal-analisis", "is_open"),
        Input("lv-abrir-analisis", "n_clicks"),
        Input("lv-cerrar-analisis", "n_clicks"),
        State("lv-modal-analisis", "is_open"),
        prevent_initial_call=True,
    )
    def abrir_cerrar_analisis(_abrir, _cerrar, abierto):
        if ctx.triggered_id == "lv-abrir-analisis":
            return True
        if ctx.triggered_id == "lv-cerrar-analisis":
            return False
        return abierto

    @app.callback(
        Output("lv-analisis-slider", "max"),
        Output("lv-analisis-slider", "marks"),
        Output("lv-analisis-slider", "value"),
        Input("lv-animacion-datos", "data"),
    )
    def configurar_tiempo(datos):
        if not datos or not datos.get("tiempo_completo"):
            return 40, {0: "0", 10: "10", 20: "20", 30: "30", 40: "40"}, 0
        fin = float(datos["tiempo_completo"][-1])
        marcas = {round(fin * j / 4, 2): f"{fin * j / 4:g}" for j in range(5)}
        return fin, marcas, 0

    @app.callback(
        Output("lv-analisis-resultado", "children"),
        Output("lv-analisis-tiempo", "children"),
        Output("lv-analisis-control-tiempo", "style"),
        Input("lv-analisis-slider", "value"),
        Input("lv-analisis-vista", "value"),
        Input("lv-animacion-datos", "data"),
        Input("lv-alpha", "value"),
        Input("lv-beta", "value"),
        Input("lv-gamma", "value"),
        Input("lv-delta", "value"),
        Input("lv-k", "value"),
        Input("lv-modelo-seleccionado", "data"),
    )
    def calcular_analisis(t, vista, datos, alpha, beta, gamma, delta, k, modelo):
        visible = {"marginBottom": "18px"}
        oculto = {"display": "none"}
        if not datos or not datos.get("tiempo_completo"):
            return (
                "Sin datos de simulación.",
                "",
                oculto if vista == "completa" else visible,
            )
        tiempos = np.asarray(datos["tiempo_completo"], dtype=float)
        presas = np.asarray(datos["presas_completas"], dtype=float)
        depredadores = np.asarray(datos["depredadores_completos"], dtype=float)
        if (
            len(tiempos) < 2
            or len(tiempos) != len(presas)
            or len(tiempos) != len(depredadores)
        ):
            return "Datos incompletos.", "", visible

        x0, y0 = float(presas[0]), float(depredadores[0])
        xeq = float(gamma / delta)
        coexistencia = modelo != "logistico" or k > xeq
        if modelo == "logistico":
            if coexistencia:
                yeq = float(alpha / beta * (1.0 - xeq / k))
            else:
                xeq, yeq = float(k), 0.0
        else:
            yeq = float(alpha / beta)

        if vista == "completa":
            return (
                _vista_completa(
                    modelo,
                    tiempos,
                    presas,
                    depredadores,
                    xeq,
                    yeq,
                    coexistencia,
                    alpha,
                    beta,
                    gamma,
                    delta,
                    k,
                ),
                "",
                oculto,
            )

        t = float(np.clip(t if t is not None else tiempos[0], tiempos[0], tiempos[-1]))
        x = float(np.interp(t, tiempos, presas))
        y = float(np.interp(t, tiempos, depredadores))
        dx = (
            alpha * x * (1 - x / k) - beta * x * y
            if modelo == "logistico"
            else alpha * x - beta * x * y
        )
        dy = delta * x * y - gamma * y
        variacion_x = 100.0 * (x / x0 - 1) if x0 else None
        variacion_y = 100.0 * (y / y0 - 1) if y0 else None
        distancia = _distancia_relativa(x, y, xeq, yeq)
        nombre_eq = (
            "equilibrio de coexistencia"
            if coexistencia
            else "equilibrio sin depredadores"
        )

        resultado = html.Div(
            [
                _seccion(
                    "Presas",
                    _indicador(
                        "Variación desde el inicio",
                        _texto_porcentaje(variacion_x),
                        _formula_variacion("x"),
                        ANCHO_TARJETA_VARIACION,
                        color_valor=PRESAS,
                    ),
                    _indicador(
                        "Tasa x′(t)",
                        _texto_tasa(dx),
                        _formula_dx(modelo),
                        ANCHO_TARJETA_TASA,
                        _estado_tasa(dx),
                        color_valor=PRESAS,
                    ),
                ),
                _seccion(
                    "Depredadores",
                    _indicador(
                        "Variación desde el inicio",
                        _texto_porcentaje(variacion_y),
                        _formula_variacion("y"),
                        ANCHO_TARJETA_VARIACION,
                        color_valor=DEPREDADORES,
                    ),
                    _indicador(
                        "Tasa y′(t)",
                        _texto_tasa(dy),
                        r"y'(t)=\delta xy-\gamma y",
                        ANCHO_TARJETA_TASA,
                        _estado_tasa(dy),
                        color_valor=DEPREDADORES,
                    ),
                ),
                _parte_inferior(
                    _indicador(
                        "Distancia relativa",
                        ("No definida" if distancia is None else f"{distancia:.1f}%"),
                        _formula_distancia(),
                        ANCHO_TARJETA_DISTANCIA,
                    ),
                    nombre_eq,
                ),
                html.Div(
                    "Una población inferior a 1 es positiva matemáticamente, "
                    "pero no representa literalmente una fracción de individuo.",
                    style={"fontSize": "11px", "color": GRIS, "marginTop": "8px"},
                )
                if x < 1 or y < 1
                else None,
            ],
            style={"width": "100%", "maxWidth": f"{ANCHO_CONTENIDO}px", "minWidth": 0},
        )

        resumen_tiempo = (
            f"Instante seleccionado: t = {t:.2f}  ·  "
            f"Presas: {x:.2f}  ·  Depredadores: {y:.2f}"
        )
        # Indicacion contextual sin recargar las tarjetas de resultados.
        # No aparece solo por tener una tasa casi cero: exige un extremo detectado.
        avisos_extremos = []
        for nombre_poblacion, serie in (
            ("presas", presas),
            ("depredadores", depredadores),
        ):
            extremo = _extremo_local_cercano(t, tiempos, serie)
            if extremo is not None:
                avisos_extremos.append(
                    html.Span(
                        f"Cerca de un {extremo} local de {nombre_poblacion}",
                        style={
                            "display": "inline-block",
                            "padding": "3px 8px",
                            "border": "1px solid #DCE4EB",
                            "background": "#F3F5F7",
                            "borderRadius": "7px",
                            "fontSize": "11px",
                            "fontWeight": 600,
                            "color": "#454545",
                        },
                    )
                )
        etiqueta_tiempo = html.Div(
            [
                html.Span(resumen_tiempo),
                html.Div(
                    avisos_extremos,
                    style={
                        "display": "flex",
                        "gap": "6px",
                        "flexWrap": "wrap",
                        "marginTop": "4px",
                    },
                )
                if avisos_extremos
                else None,
            ]
        )
        return resultado, etiqueta_tiempo, visible
