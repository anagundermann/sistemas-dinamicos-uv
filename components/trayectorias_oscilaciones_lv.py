"""Teoria de trayectorias y oscilaciones para Lotka-Volterra.

Este modal es exclusivamente teorico: nunca calcula resultados del escenario.
Conserva las cinco tarjetas originales, dos columnas y clases CSS.
La vista de Analisis de la dinamica calcula los indicadores numericos.
"""

from dash import dcc, html


def formula(tex, clase=""):
    """Presenta expresiones LaTeX mediante MathJax."""
    clases = "lv-ciclos-formula"
    if clase:
        clases += f" {clase}"
    return dcc.Markdown(tex, mathjax=True, className=clases)


def _tarjeta(clase, titulo, *contenido):
    return html.Article(
        className=f"lv-ciclos-tarjeta {clase}",
        children=[html.H4(titulo), *contenido],
    )


def _nota(texto):
    return html.P(texto, className="lv-ciclos-nota")


def _columna(titulo, tarjetas):
    return html.Section(
        className="lv-ciclos-columna",
        children=[html.H3(titulo, className="lv-ciclos-grupo"), *tarjetas],
    )


def _contenido_clasico():
    """Cinco tarjetas de teoria del modelo clasico, sin resultados numericos."""
    izquierda = _columna(
        "Medicion de las oscilaciones",
        [
            _tarjeta(
                "lv-ciclos-maximos",
                "Máximos y mínimos locales",
                html.P("Para z(t)=x(t) o z(t)=y(t), en un extremo no degenerado:"),
                formula(
                    r"$$z'(t_i)=0,\qquad\begin{cases}z''(t_i)<0 & \text{máximo}\\ z''(t_i)>0 & \text{mínimo}\end{cases}$$",
                    "lv-ciclos-formula-extremos",
                ),
                _nota(
                    "La derivada se anula y la segunda determina el tipo de extremo. Son condiciones suficientes para extremos no degenerados."
                ),
            ),
            _tarjeta(
                "lv-ciclos-periodos",
                "Períodos observados",
                html.P(
                    "Entre máximos consecutivos de la misma población:",
                    className="lv-ciclos-etiqueta",
                ),
                formula(r"$$T_i=t_{i+1}-t_i$$"),
                html.P("Promedio de los intervalos:", className="lv-ciclos-etiqueta"),
                formula(
                    r"$$\widehat T=\frac{t_n-t_1}{n-1},\quad n\geq2$$",
                    "lv-ciclos-formula-promedio",
                ),
                _nota(
                    "Se promedian separaciones temporales, no alturas de los máximos. La estimación exige al menos dos máximos."
                ),
            ),
        ],
    )
    derecha = _columna(
        "Relaciones y aproximaciones",
        [
            _tarjeta(
                "lv-ciclos-supuestos",
                "Desfase entre presas y depredadores",
                formula(r"$$\Delta t_i=t_{i,\max}^{(y)}-t_{i,\max}^{(x)}$$"),
                _nota(
                    "Compara el máximo de depredadores que sigue al máximo de presas en el mismo ciclo. Un desfase positivo significa que los depredadores alcanzan el pico después."
                ),
            ),
            _tarjeta(
                "lv-ciclos-aproximacion",
                "Aproximación cerca del equilibrio",
                formula(r"$$T_{\mathrm{lin}}=\frac{2\pi}{\sqrt{\alpha\gamma}}$$"),
                _nota(
                    "Período de la linealización alrededor del centro de coexistencia. Aproxima las oscilaciones pequeñas; las de mayor amplitud pueden tener otro período."
                ),
            ),
            _tarjeta(
                "lv-ciclos-equivalentes",
                "Ciclos equivalentes en un intervalo",
                formula(r"$$N_{\mathrm{equiv}}\approx\frac{t_f-t_0}{\widehat T}$$"),
                _nota(
                    "Cuantifica cuántos períodos estimados caben en la duración observada. No equivale necesariamente a contar vueltas completas desde el inicio."
                ),
            ),
        ],
    )
    return html.Div(
        className="lv-ciclos",
        children=[
            html.Div(className="lv-ciclos-columnas", children=[izquierda, derecha])
        ],
    )


def _contenido_logistico():
    """Teoria general de oscilaciones transitorias del modelo logistico."""
    izquierda = _columna(
        "Extremos y oscilaciones transitorias",
        [
            _tarjeta(
                "lv-ciclos-maximos",
                "Máximos y mínimos locales",
                html.P(
                    "Las mismas condiciones de extremos se aplican a ambas poblaciones:"
                ),
                formula(
                    r"$$z'(t_i)=0,\qquad\begin{cases}z''(t_i)<0 & \text{máximo}\\ z''(t_i)>0 & \text{mínimo}\end{cases}$$",
                    "lv-ciclos-formula-extremos",
                ),
                _nota(
                    "Los extremos pueden aparecer durante una oscilación amortiguada. Su existencia no demuestra una órbita periódica."
                ),
            ),
            _tarjeta(
                "lv-ciclos-periodos",
                "Separación entre picos transitorios",
                html.P("Si existen al menos dos máximos consecutivos:"),
                formula(
                    r"$$\Delta t_i=t_{i+1}-t_i,\qquad\overline{\Delta t}=\frac{t_n-t_1}{n-1}$$",
                    "lv-ciclos-formula-promedio",
                ),
                _nota(
                    "Es una separación temporal observada, no el período de una órbita cerrada. Si no hay dos máximos, no puede estimarse."
                ),
            ),
        ],
    )
    derecha = _columna(
        "Desfase, escalas y amortiguamiento",
        [
            _tarjeta(
                "lv-ciclos-supuestos",
                "Desfase temporal entre poblaciones",
                formula(r"$$\Delta t_i=t_{i,\max}^{(y)}-t_{i,\max}^{(x)}$$"),
                _nota(
                    "Compara máximos de presas y depredadores correspondientes a una misma oscilación. En ausencia de picos comparables, el desfase no se estima."
                ),
            ),
            _tarjeta(
                "lv-ciclos-aproximacion",
                "Oscilación y decaimiento cerca del equilibrio",
                formula(
                    r"$$\omega=\sqrt{\det J_*-\frac{(\operatorname{tr}J_*)^2}{4}}$$"
                ),
                formula(
                    r"$$T_{\mathrm{lin}}=\frac{2\pi}{\omega},\qquad\tau=-\frac{2}{\operatorname{tr}J_*}$$"
                ),
                _nota(
                    "Estas fórmulas se aplican a una coexistencia con foco estable: frecuencia real positiva y traza negativa. Si el equilibrio es un nodo, no hay período local oscilatorio."
                ),
            ),
            _tarjeta(
                "lv-ciclos-equivalentes",
                "Amplitud y ausencia de ciclos permanentes",
                formula(r"$$A_i=\left|x(t_i^{\max})-x_*\right|$$"),
                formula(r"$$R_i=\left(1-\frac{A_{i+1}}{A_i}\right)100\%$$"),
                _nota(
                    "Si Rᵢ > 0, la amplitud medida disminuye entre esos dos máximos (Aᵢ > 0). Las espirales amortiguadas no son órbitas periódicas persistentes."
                ),
            ),
        ],
    )
    return html.Div(
        className="lv-ciclos",
        children=[
            html.Div(className="lv-ciclos-columnas", children=[izquierda, derecha])
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
    """La interfaz conserva sus argumentos; la teoria no usa sliders."""
    if modelo_seleccionado == "logistico":
        return _contenido_logistico()
    return _contenido_clasico()
