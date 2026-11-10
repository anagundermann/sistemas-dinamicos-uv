"""Modal Trayectorias y oscilaciones para los modelos depredador-presa.

Conserva las cinco tarjetas originales del modelo clasico y utiliza
las mismas clases CSS para las cinco tarjetas del modelo logistico.
No modifica los modelos, la animacion ni los callbacks de la pagina.
"""

from dash import dcc, html


def formula(tex, clase=""):
    """Muestra una fórmula LaTeX mediante MathJax."""
    clases = "lv-ciclos-formula"
    if clase:
        clases += f" {clase}"
    return dcc.Markdown(tex, mathjax=True, className=clases)


def _crear_contenido_clasico():
    """Conserva las cinco tarjetas del modelo clasico sin cambios."""
    return html.Div(
        className="lv-ciclos",
        children=[
            html.Div(
                className="lv-ciclos-columnas",
                children=[
                    # Columna izquierda: determinación del período.
                    html.Section(
                        className="lv-ciclos-columna",
                        children=[
                            html.H3(
                                "Determinación del período",
                                className="lv-ciclos-grupo",
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-maximos",
                                children=[
                                    html.H4("Máximos de presas"),
                                    html.P(
                                        "En los tiempos t₁ < t₂ < ··· < tₙ, "
                                        "un máximo local no degenerado satisface:"
                                    ),
                                    formula(
                                        r"$$x'(t_i)=0,\qquad x''(t_i)<0$$",
                                        "lv-ciclos-formula-maximos",
                                    ),
                                    html.P(
                                        "La primera derivada se anula; la segunda "
                                        "negativa permite identificar un máximo local.",
                                        className="lv-ciclos-nota",
                                    ),
                                ],
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-periodos",
                                children=[
                                    html.H4("Períodos observados"),
                                    html.P(
                                        "Entre dos máximos consecutivos",
                                        className="lv-ciclos-etiqueta",
                                    ),
                                    formula(r"$$T_i=t_{i+1}-t_i$$"),
                                    html.P(
                                        "Período estimado promedio",
                                        className="lv-ciclos-etiqueta",
                                    ),
                                    formula(
                                        r"$$\widehat T=\frac{1}{n-1}"
                                        r"\sum_{i=1}^{n-1}T_i="
                                        r"\frac{t_n-t_1}{n-1}$$",
                                        "lv-ciclos-formula-promedio",
                                    ),
                                    html.P(
                                        [
                                            "Se promedian los ",
                                            html.Strong("intervalos de tiempo"),
                                            " entre máximos, no los valores máximos "
                                            "de la población.",
                                        ],
                                        className="lv-ciclos-nota lv-ciclos-nota-separada",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Columna derecha: condiciones, aproximación y ciclos.
                    html.Section(
                        className="lv-ciclos-columna",
                        children=[
                            html.H3(
                                "Condiciones y aproximaciones",
                                className="lv-ciclos-grupo",
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-supuestos",
                                children=[
                                    html.H4("Supuestos del cálculo"),
                                    html.Div(
                                        className="lv-ciclos-supuestos-grid",
                                        children=[
                                            html.Div(
                                                className="lv-ciclos-supuesto",
                                                children=[
                                                    html.Span(
                                                        "Intervalo de simulación"
                                                    ),
                                                    html.Strong(
                                                        [
                                                            "[t₀, t",
                                                            html.Sub("f"),
                                                            "] = [0, 40]",
                                                        ],
                                                        className="lv-ciclos-matematica-inline",
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="lv-ciclos-supuesto",
                                                children=[
                                                    html.Span("Población analizada"),
                                                    html.Strong("Presas x(t)"),
                                                ],
                                            ),
                                            html.Div(
                                                className="lv-ciclos-supuesto",
                                                children=[
                                                    html.Span("Mínimo requerido"),
                                                    html.Strong(
                                                        "Dos máximos consecutivos"
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                className="lv-ciclos-supuesto",
                                                children=[
                                                    html.Span("Solución numérica"),
                                                    html.Strong("RK45 · SciPy"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-aproximacion",
                                children=[
                                    html.H4("Aproximación cerca del equilibrio"),
                                    html.Div(
                                        className="lv-ciclos-explicacion-lateral",
                                        children=[
                                            formula(
                                                r"$$T_{\mathrm{lin}}="
                                                r"\frac{2\pi}{\sqrt{\alpha\gamma}}$$"
                                            ),
                                            html.P(
                                                [
                                                    "Válida para ",
                                                    html.Strong(
                                                        "oscilaciones pequeñas"
                                                    ),
                                                    " cerca del equilibrio de coexistencia.",
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-equivalentes",
                                children=[
                                    html.H4("Ciclos equivalentes en la simulación"),
                                    formula(
                                        r"$$N_{\mathrm{equiv}}\approx"
                                        r"\frac{t_f-t_0}{\widehat T}="
                                        r"\frac{40}{\widehat T}$$",
                                        "lv-ciclos-formula-equivalentes",
                                    ),
                                    html.P(
                                        [
                                            "Aquí ",
                                            html.Strong(
                                                "40 es la duración de la simulación"
                                            ),
                                            ", no el período. El resultado representa "
                                            "ciclos equivalentes, no necesariamente "
                                            "vueltas completas desde t = 0.",
                                        ],
                                        className="lv-ciclos-nota",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def _crear_supuesto(etiqueta, valor):
    """Una celda del recuadro de condiciones, con el CSS existente."""
    return html.Div(
        className="lv-ciclos-supuesto",
        children=[html.Span(etiqueta), html.Strong(valor)],
    )


def crear_contenido_trayectorias_logistico(alpha, beta, gamma, delta, k):
    """Contenido del modelo con crecimiento logistico de las presas.

    Clasifica el comportamiento local en foco, nodo o ausencia de
    coexistencia; no confunde oscilaciones transitorias con ciclos.
    """
    alpha, beta, gamma, delta, k = map(float, (alpha, beta, gamma, delta, k))
    if min(alpha, beta, gamma, delta, k) <= 0:
        raise ValueError("Los parametros deben ser positivos.")

    x_critico = gamma / delta
    umbral = abs(delta * k - gamma) <= 1e-10
    coexistencia = (k > x_critico) and not umbral

    if coexistencia:
        x_estrella = x_critico
        y_estrella = alpha / beta * (1.0 - x_estrella / k)
        traza = -alpha * x_estrella / k
        determinante = alpha * gamma * (1.0 - x_estrella / k)
        discriminante = traza**2 - 4.0 * determinante
        tolerancia = 1e-9 * max(1.0, abs(traza**2), abs(4.0 * determinante))
        foco = discriminante < -tolerancia
        nodo = not foco

        formula_destino = (
            r"$$E_* = \left(\frac{\gamma}{\delta},"
            r"\frac{\alpha}{\beta}"
            r"\left(1-\frac{\gamma}{\delta K}\right)\right)$$"
        )
        descripcion_destino = (
            f"Con estos parámetros: x* ≈ {x_estrella:.1f} y "
            f"y* ≈ {y_estrella:.1f}. Las soluciones positivas "
            "se aproximan al equilibrio de coexistencia."
        )
        tipo = "Foco estable" if foco else "Nodo estable"
        condicion = "K > γ/δ"
    else:
        foco = False
        nodo = False
        formula_destino = r"$$E_F=(K,0)$$"
        descripcion_destino = (
            f"Con K = {k:g}, no existe coexistencia positiva. "
            "Las presas se aproximan a K y los depredadores a cero."
        )
        tipo = "Umbral no hiperbólico" if umbral else "Sin coexistencia"
        condicion = "K = γ/δ" if umbral else "K < γ/δ"

    if foco:
        titulo_oscilaciones = "Oscilaciones amortiguadas"
        formula_oscilaciones = (
            r"$$\lambda_\pm=\frac{\operatorname{tr}J_*}{2}"
            r"\pm i\omega$$"
        )
        descripcion_oscilaciones = (
            "Cerca del equilibrio, la parte real negativa de los "
            "autovalores reduce la amplitud: la espiral se cierra "
            "hacia el punto, no forma un ciclo persistente."
        )
        titulo_aproximacion = "Escala local de oscilación"
        formula_aproximacion = r"$$T_{\mathrm{lin}}=\frac{2\pi}{\omega}$$"
        nota_aproximacion = (
            r"$\omega^2=\det J_*-\frac{(\operatorname{tr}J_*)^2}{4}>0$. "
            "Es la escala de las oscilaciones amortiguadas cerca "
            "del equilibrio; no un período de órbita cerrada."
        )
        titulo_ultima = "Separación entre máximos"
        formula_ultima = r"$$\Delta t_i=t_{i+1}-t_i$$"
        nota_ultima = (
            "Si aparecen dos o más máximos de presas, su separación "
            "describe las oscilaciones transitorias. No implica que "
            "exista un ciclo periódico permanente."
        )
    elif nodo:
        titulo_oscilaciones = "Convergencia sin oscilaciones persistentes"
        formula_oscilaciones = r"$$D=(\operatorname{tr}J_*)^2-4\det J_*\geq 0$$"
        descripcion_oscilaciones = (
            "Cerca del equilibrio los autovalores son reales y "
            "negativos. Las perturbaciones decaen sin giros "
            "repetidos alrededor del equilibrio."
        )
        titulo_aproximacion = "Sin período de oscilación local"
        formula_aproximacion = (
            r"$$\lambda_\pm=\frac{\operatorname{tr}J_*\pm\sqrt D}{2}$$"
        )
        nota_aproximacion = (
            "Las soluciones próximas se aproximan al equilibrio. "
            "No corresponde utilizar la fórmula de período del modelo clásico."
        )
        titulo_ultima = "Lectura del plano de fases"
        formula_ultima = r"$$\lim_{t\to\infty}(x(t),y(t))=E_*$$"
        nota_ultima = (
            "La trayectoria se dirige al punto de coexistencia. "
            "Que una curva tenga un giro transitorio no significa "
            "que exista un ciclo periódico."
        )
    else:
        titulo_oscilaciones = "Desaparición de los depredadores"
        formula_oscilaciones = r"$$K\leq\frac{\gamma}{\delta}$$"
        descripcion_oscilaciones = (
            "La capacidad de carga no permite sostener depredadores "
            "a largo plazo. La trayectoria se acerca al eje de las presas."
        )
        titulo_aproximacion = (
            "Caso límite no hiperbólico"
            if umbral
            else "Equilibrio estable en la frontera"
        )
        formula_aproximacion = (
            r"$$\delta K=\gamma$$" if umbral else r"$$\delta K<\gamma$$"
        )
        nota_aproximacion = (
            "En la igualdad, la linealización tiene un autovalor cero: "
            "no basta para clasificar el equilibrio."
            if umbral
            else "Los depredadores no pueden mantenerse; la solución "
            "positiva se aproxima a (K,0)."
        )
        titulo_ultima = "Sin ciclos de coexistencia"
        formula_ultima = r"$$\lim_{t\to\infty}(x(t),y(t))=(K,0)$$"
        nota_ultima = (
            "El modelo continuo puede acercarse a cero sin alcanzar "
            "la extinción exacta en tiempo finito."
        )

    return html.Div(
        className="lv-ciclos",
        children=[
            html.Div(
                className="lv-ciclos-columnas",
                children=[
                    html.Section(
                        className="lv-ciclos-columna",
                        children=[
                            html.H3(
                                "Trayectorias con recursos limitados",
                                className="lv-ciclos-grupo",
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-maximos",
                                children=[
                                    html.H4("Destino de las poblaciones"),
                                    formula(formula_destino),
                                    html.P(
                                        descripcion_destino,
                                        className="lv-ciclos-nota",
                                    ),
                                ],
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-periodos",
                                children=[
                                    html.H4(titulo_oscilaciones),
                                    formula(formula_oscilaciones),
                                    html.P(
                                        descripcion_oscilaciones,
                                        className="lv-ciclos-nota",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Section(
                        className="lv-ciclos-columna",
                        children=[
                            html.H3(
                                "Condiciones y aproximaciones",
                                className="lv-ciclos-grupo",
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-supuestos",
                                children=[
                                    html.H4("Condiciones del escenario"),
                                    html.Div(
                                        className="lv-ciclos-supuestos-grid",
                                        children=[
                                            _crear_supuesto("Intervalo", "[0, 40]"),
                                            _crear_supuesto("Comportamiento", tipo),
                                            _crear_supuesto("Condición", condicion),
                                            _crear_supuesto(
                                                "Integración", "RK45 · SciPy"
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-aproximacion",
                                children=[
                                    html.H4(titulo_aproximacion),
                                    html.Div(
                                        className="lv-ciclos-explicacion-lateral",
                                        children=[
                                            formula(formula_aproximacion),
                                            formula(
                                                nota_aproximacion,
                                                "lv-ciclos-nota",
                                            )
                                            if foco
                                            else html.P(
                                                nota_aproximacion,
                                                className="lv-ciclos-nota",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Article(
                                className="lv-ciclos-tarjeta lv-ciclos-equivalentes",
                                children=[
                                    html.H4(titulo_ultima),
                                    formula(formula_ultima),
                                    html.P(
                                        nota_ultima,
                                        className="lv-ciclos-nota",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def crear_contenido_ciclos_periodo(
    modelo_seleccionado="clasico",
    alpha=0.65,
    beta=0.018,
    gamma=0.55,
    delta=0.012,
    k=120,
):
    """Selecciona la teoria del modelo activo; mantiene la API anterior."""
    if modelo_seleccionado == "logistico":
        return crear_contenido_trayectorias_logistico(alpha, beta, gamma, delta, k)
    return _crear_contenido_clasico()
