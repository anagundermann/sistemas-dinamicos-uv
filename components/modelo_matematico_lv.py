"""Contenido compacto del modal «Modelo matemático · Lotka–Volterra».

Solo modifica la presentación del modelo. Reutiliza el modal compartido
que ya existe en pages/depredador_presa.py, sin alterar sus callbacks.
"""

from dash import dcc, html


def texto_matematico(texto, clase=None):
    """Renderiza expresiones LaTeX, incluso dentro de frases."""
    return dcc.Markdown(texto, mathjax=True, className=clase)


def crear_tarjeta_ecuacion(especie, titulo, formula, explicacion):
    """Muestra una EDO en una tarjeta compacta."""
    return html.Section(
        className=f"lv-mat-ecuacion lv-mat-{especie}",
        children=[
            html.H4(titulo),
            texto_matematico(formula, "lv-mat-formula"),
            html.P(explicacion, className="lv-mat-nota-ecuacion"),
        ],
    )


def crear_tarjeta_variable(simbolo, descripcion):
    """Muestra una variable de estado con notación matemática."""
    return html.Div(
        className="lv-mat-variable",
        children=[
            texto_matematico(f"${simbolo}$", "lv-mat-variable-simbolo"),
            html.P(descripcion),
        ],
    )


def crear_parametro(simbolo, titulo, descripcion):
    """Muestra un parámetro positivo del sistema."""
    return html.Div(
        className="lv-mat-parametro",
        children=[
            texto_matematico(f"${simbolo}$", "lv-mat-simbolo"),
            html.Div(
                className="lv-mat-parametro-texto",
                children=[
                    html.Strong(titulo),
                    html.P(descripcion),
                ],
            ),
        ],
    )


def crear_contenido_modelo_matematico():
    """Cuerpo del modal: EDO lado a lado, condiciones iniciales y parámetros."""
    return html.Div(
        className="lv-mat",
        children=[
            html.Div(
                className="lv-mat-columnas",
                children=[
                    # COLUMNA IZQUIERDA
                    html.Section(
                        className="lv-mat-columna",
                        children=[
                            html.H3("Sistema de ecuaciones"),
                            html.Div(
                                className="lv-mat-ecuaciones",
                                children=[
                                    crear_tarjeta_ecuacion(
                                        "presas",
                                        "Presas · Conejos",
                                        r"$$\frac{dx}{dt}=\alpha x-\beta xy$$",
                                        "Crecimiento − depredación",
                                    ),
                                    crear_tarjeta_ecuacion(
                                        "depredadores",
                                        "Depredadores · Zorros",
                                        r"$$\frac{dy}{dt}=\delta xy-\gamma y$$",
                                        "Reproducción − mortalidad",
                                    ),
                                    html.Section(
                                        className="lv-mat-iniciales",
                                        children=[
                                            html.H4("Condiciones iniciales"),
                                            html.Div(
                                                className="lv-mat-iniciales-formulas",
                                                children=[
                                                    texto_matematico(
                                                        r"$x(0)=x_0$",
                                                        "lv-mat-inicial-formula",
                                                    ),
                                                    texto_matematico(
                                                        r"$y(0)=y_0$",
                                                        "lv-mat-inicial-formula",
                                                    ),
                                                ],
                                            ),
                                            html.P(
                                                "Poblaciones de conejos y zorros al comenzar la simulación."
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="lv-mat-idea",
                                children=[
                                    texto_matematico(
                                        r"El producto $xy$ representa la interacción entre presas y depredadores.",
                                        "lv-mat-idea-texto",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # COLUMNA DERECHA
                    html.Section(
                        className="lv-mat-columna lv-mat-columna-derecha",
                        children=[
                            html.H3("Variables y parámetros"),
                            html.Div(
                                className="lv-mat-variables",
                                children=[
                                    crear_tarjeta_variable(
                                        "x(t)", "Población de conejos"
                                    ),
                                    crear_tarjeta_variable(
                                        "y(t)", "Población de zorros"
                                    ),
                                ],
                            ),
                            texto_matematico(
                                r"$t$: tiempo. Los parámetros $\alpha$, $\beta$, $\gamma$ y $\delta$ son positivos.",
                                "lv-mat-tiempo",
                            ),
                            html.Div(
                                className="lv-mat-parametros",
                                children=[
                                    crear_parametro(
                                        r"\alpha",
                                        "Crecimiento",
                                        "Crecimiento natural de presas",
                                    ),
                                    crear_parametro(
                                        r"\beta",
                                        "Depredación",
                                        "Pérdidas de presas",
                                    ),
                                    crear_parametro(
                                        r"\gamma",
                                        "Mortalidad",
                                        "Mortalidad natural de zorros",
                                    ),
                                    crear_parametro(
                                        r"\delta",
                                        "Reproducción",
                                        "Aumento debido a las presas",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
