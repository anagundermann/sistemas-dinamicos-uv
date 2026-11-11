"""Analisis cuantitativo de Lotka-Volterra (clasico y logistico).

La pagina principal ya importa estas tres funciones:
    crear_boton_analisis_lv
    crear_modal_analisis_lv
    registrar_callbacks_analisis_lv

Solo consulta los resultados de lv-animacion-datos. No modifica Play.
"""

import numpy as np
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
PROPORCION_DISTANCIA = 1.50
PROPORCION_INTERPRETACION = 0.50
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


def _indicador(etiqueta, valor, formula, ancho_tarjeta, estado=""):
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
                    "color": AZUL,
                    "marginTop": "4px",
                },
            ),
            html.Div(
                estado,
                style={
                    "fontSize": "12px",
                    "fontWeight": 700,
                    "color": ("#a34f18" if estado == "Disminuyendo" else PRESAS),
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
                    "color": AZUL,
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
                "Si una tasa es cero, el cambio instantáneo de esa población "
                "es nulo; no implica equilibrio.",
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
    return html.Div(
        [
            html.Div(titulo, style={"fontSize": "12px", "color": GRIS}),
            html.Div(
                valor, style={"fontSize": "20px", "fontWeight": 700, "color": AZUL}
            ),
        ],
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
        "Análisis cuantitativo",
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
                dbc.ModalTitle("Análisis cuantitativo"),
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


def _estado_tasa(valor):
    if valor > 1e-8:
        return "Aumentando"
    if valor < -1e-8:
        return "Disminuyendo"
    return "Tasa prácticamente nula"


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
    }


def _vista_completa(
    modelo,
    tiempos,
    presas,
    depredadores,
    xeq,
    yeq,
    coexistencia,
    alpha,
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

    resultado_maximos = _maximos_presas(tiempos, presas, xeq)
    periodo = resultado_maximos["periodo"]
    n_maximos = resultado_maximos["maximos"]
    n_ciclos = resultado_maximos["ciclos"]

    contenido = [
        _bloque_completo(
            "Equilibrio de coexistencia"
            if coexistencia
            else "Equilibrio sin depredadores",
            [("Presas x*", f"{xeq:.2f}"), ("Depredadores y*", f"{yeq:.2f}")],
            nota=f"Intervalo analizado: t = {tiempos[0]:g} a {tiempos[-1]:g}.",
        ),
    ]

    if modelo == "clasico":
        t_lineal = 2.0 * np.pi / np.sqrt(alpha * gamma)
        contenido.append(
            _bloque_completo(
                "Ciclos y período observado",
                [
                    ("Máximos locales de presas", str(n_maximos)),
                    ("Ciclos pico a pico", str(n_ciclos)),
                    (
                        "Período medio observado",
                        f"{periodo:.2f}" if periodo else "No estimable",
                    ),
                ],
                formula=(
                    r"\widehat T=\frac{t_n-t_1}{n-1}",
                    r"T_i=t_{i+1}-t_i",
                ),
                nota=(
                    "Se necesitan al menos dos máximos. Cada ciclo contado corresponde "
                    "al intervalo entre dos máximos consecutivos de presas."
                ),
            )
        )
        contenido.append(
            _bloque_completo(
                "Referencia cerca del equilibrio",
                [
                    ("Período lineal aproximado", f"{t_lineal:.2f}"),
                    (
                        "Ciclos equivalentes en el intervalo",
                        f"{duracion / periodo:.2f}" if periodo else "No estimable",
                    ),
                ],
                formula=(
                    r"T_{\mathrm{lin}}=\frac{2\pi}{\sqrt{\alpha\gamma}}",
                    r"N_{\mathrm{equiv}}\approx\frac{t_f-t_0}{\widehat T}",
                ),
                nota=(
                    "Órbita periódica cerrada, sin amortiguamiento. T_lin aproxima "
                    "el período de oscilaciones pequeñas; el período observado puede diferir."
                ),
            )
        )

    elif coexistencia:
        # Misma clasificacion local del modal Trayectorias y oscilaciones.
        traza = -alpha * xeq / k
        determinante = alpha * gamma * (1.0 - xeq / k)
        discriminante = traza**2 - 4.0 * determinante
        tolerancia = 1e-9 * max(1.0, abs(traza**2), abs(4.0 * determinante))

        if discriminante < -tolerancia:
            omega = np.sqrt(determinante - traza**2 / 4.0)
            t_lineal = 2.0 * np.pi / omega
            tau = -2.0 / traza
            contenido.append(
                _bloque_completo(
                    "Comportamiento local · Foco estable",
                    [
                        ("Máximos de presas", str(n_maximos)),
                        ("Intervalos pico a pico", str(n_ciclos)),
                        (
                            "Separación media observada",
                            f"{periodo:.2f}" if periodo else "No estimable",
                        ),
                    ],
                    formula=r"\widehat T=\frac{t_n-t_1}{n-1}",
                    nota=(
                        "Espiral amortiguada: los máximos describen oscilaciones "
                        "transitorias, no ciclos periódicos permanentes."
                    ),
                )
            )
            # Valor propio complejo conjugado: justifica el foco estable.
            parte_real = traza / 2.0
            contenido.append(
                _bloque_completo(
                    "Autovalores del jacobiano · Foco estable",
                    [
                        ("Autovalores λ₁,₂", f"{parte_real:+.4f} ± {omega:.4f}i"),
                        ("Trayectoria local", "Espiral amortiguada"),
                    ],
                    formula=(
                        r"\lambda_{1,2}=\frac{\operatorname{tr}J_*}{2}\pm i\omega",
                        rf"\lambda_{{1,2}}\approx {parte_real:+.4f} \pm {omega:.4f}i",
                    ),
                    nota=(
                        "Parte real negativa: la amplitud se amortigua. "
                        "Parte imaginaria distinta de cero: la solución gira cerca "
                        "del equilibrio. Es una clasificación local, no una "
                        "afirmación de que la espiral se vea completa en t = 0 a 40."
                    ),
                )
            )
            contenido.append(
                _bloque_completo(
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
                    formula=(
                        r"\omega=\sqrt{\det J_*-\frac{(\operatorname{tr}J_*)^2}{4}}",
                        r"T_{\mathrm{lin}}=\frac{2\pi}{\omega}",
                        r"\tau=-\frac{2}{\operatorname{tr}J_*}",
                    ),
                    nota=(
                        "T_lin y τ son aproximaciones locales: τ es la escala para "
                        "reducir la amplitud aproximadamente a 1/e cerca del equilibrio. "
                        "La reducción observada usa |máximo de presas − x*|; "
                        "puede ser negativa si la amplitud crece en el intervalo."
                    ),
                )
            )
        else:
            raiz = np.sqrt(max(discriminante, 0.0))
            lambda_lenta = (traza + raiz) / 2.0
            tiempo_relajacion = -1.0 / lambda_lenta if lambda_lenta < -1e-12 else None
            contenido.append(
                _bloque_completo(
                    "Comportamiento local · Nodo estable",
                    [
                        ("Período de oscilación local", "No corresponde"),
                        ("Autovalor de decaimiento más lento", f"{lambda_lenta:.4f}"),
                        (
                            "Tiempo característico de relajación",
                            f"{tiempo_relajacion:.2f}"
                            if tiempo_relajacion
                            else "No estimable",
                        ),
                    ],
                    formula=(
                        r"D=(\operatorname{tr}J_*)^2-4\det J_*\geq 0",
                        r"\lambda_+=\frac{\operatorname{tr}J_*+\sqrt D}{2}",
                        r"\tau=-\frac{1}{\lambda_+}",
                    ),
                    nota=(
                        "Cerca del equilibrio hay convergencia sin giros repetidos. "
                        "τ es una escala local de relajación, no el tiempo exacto "
                        "en que se alcanza el equilibrio."
                    ),
                )
            )
    else:
        tasa_borde = delta * k - gamma
        condicion = "K = γ/δ" if abs(tasa_borde) <= 1e-10 else "K < γ/δ"
        contenido.append(
            _bloque_completo(
                "Sin equilibrio positivo de coexistencia",
                [
                    ("Condición del modelo", condicion),
                    ("Tasa de depredadores cerca de (K, 0)", f"{tasa_borde:+.4f}"),
                    ("Período de coexistencia", "No corresponde"),
                ],
                formula=(
                    r"E_F=(K,0)",
                    r"\frac{y'}{y}\approx\delta K-\gamma",
                ),
                nota=(
                    "La solución tiende al equilibrio sin depredadores. "
                    "En el umbral K = γ/δ la tasa lineal se anula y la "
                    "clasificación requiere un análisis adicional."
                ),
            )
        )

    contenido.extend(
        [
            _bloque_completo(
                "Distancia relativa al equilibrio",
                [
                    (
                        "Al inicio",
                        f"{distancia_inicial:.1f}%"
                        if distancia_inicial is not None
                        else "No definida",
                    ),
                    (
                        f"Al final (t = {tiempos[-1]:g})",
                        f"{distancia_final:.1f}%"
                        if distancia_final is not None
                        else "No definida",
                    ),
                ],
                formula=_formula_distancia(),
                nota=("Esta distancia compara posiciones respecto del equilibrio; "),
            ),
            _bloque_completo(
                "Variación total respecto del inicio",
                [
                    ("Presas", _texto_porcentaje(variacion_x)),
                    ("Depredadores", _texto_porcentaje(variacion_y)),
                ],
                formula=(
                    r"\Delta_x=\frac{x(t_f)-x_0}{x_0}\cdot100\%",
                    r"\Delta_y=\frac{y(t_f)-y_0}{y_0}\cdot100\%",
                ),
            ),
        ]
    )
    return html.Div(contenido, style={"minWidth": 0})


def registrar_callbacks_analisis_lv(app):
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
                    ),
                    _indicador(
                        "Tasa x′(t)",
                        f"{dx:+.3f}",
                        _formula_dx(modelo),
                        ANCHO_TARJETA_TASA,
                        _estado_tasa(dx),
                    ),
                ),
                _seccion(
                    "Depredadores",
                    _indicador(
                        "Variación desde el inicio",
                        _texto_porcentaje(variacion_y),
                        _formula_variacion("y"),
                        ANCHO_TARJETA_VARIACION,
                    ),
                    _indicador(
                        "Tasa y′(t)",
                        f"{dy:+.3f}",
                        r"y'(t)=\delta xy-\gamma y",
                        ANCHO_TARJETA_TASA,
                        _estado_tasa(dy),
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

        etiqueta_tiempo = (
            f"Instante seleccionado: t = {t:.2f}  ·  "
            f"Presas: {x:.2f}  ·  Depredadores: {y:.2f}"
        )
        return resultado, etiqueta_tiempo, visible
