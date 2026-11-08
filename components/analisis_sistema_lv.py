"""Modal compacto de analisis del sistema Lotka-Volterra.

Diseñado para conservar la altura de los modales Ecosistema y Modelo matematico
sin perder el contenido principal. No modifica callbacks ni las ecuaciones.
"""

from dash import dcc, html


def formula(texto, clase=""):
    """Muestra expresiones matematicas con MathJax."""
    return dcc.Markdown(texto, mathjax=True, className=clase)


def crear_equilibrio(tipo, titulo, expresion, descripcion, estabilidad):
    """Tarjeta para un punto de equilibrio."""
    return html.Section(
        className=f"lv-ana-equilibrio lv-ana-equilibrio-{tipo}",
        children=[
            html.H4(titulo),
            formula(expresion, "lv-ana-formula-equilibrio"),
            html.P(descripcion, className="lv-ana-descripcion-equilibrio"),
            html.Strong(estabilidad, className="lv-ana-estado-equilibrio"),
        ],
    )


def crear_contenido_analisis_sistema():
    """Distribuye el contenido en dos columnas equilibradas y compactas."""
    return html.Div(
        className="lv-ana lv-ana-compacto",
        children=[
            html.Div(
                className="lv-ana-columnas",
                children=[
                    # COLUMNA IZQUIERDA: puntos de equilibrio y estabilidad.
                    html.Section(
                        className="lv-ana-columna lv-ana-columna-izquierda",
                        children=[
                            html.H3("Puntos de equilibrio"),
                            html.Div(
                                className="lv-ana-equilibrios",
                                children=[
                                    crear_equilibrio(
                                        "extincion",
                                        "Extinción",
                                        r"$E_0=(0,0)$",
                                        "Punto de silla",
                                        "Inestable",
                                    ),
                                    crear_equilibrio(
                                        "coexistencia",
                                        "Coexistencia",
                                        r"$E_*=\left(\frac{\gamma}{\delta},\frac{\alpha}{\beta}\right)$",
                                        "Centro",
                                        "Estable, no asintótico",
                                    ),
                                ],
                            ),
                            html.H3(
                                "Estabilidad de coexistencia",
                                className="lv-ana-titulo-estabilidad",
                            ),
                            html.Section(
                                className="lv-ana-estabilidad-centro",
                                children=[
                                    formula(
                                        r"$\lambda_{\pm}=\pm i\sqrt{\alpha\gamma}$",
                                        "lv-ana-formula-autovalores",
                                    ),
                                    html.Div(
                                        className="lv-ana-estabilidad-definiciones",
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.Strong("Estable (Lyapunov)"),
                                                    html.P(
                                                        "Las soluciones suficientemente "
                                                        "cercanas permanecen cerca."
                                                    ),
                                                ],
                                            ),
                                            html.Div(
                                                children=[
                                                    html.Strong("No asintótico"),
                                                    html.P(
                                                        "Las soluciones próximas no "
                                                        "convergen al equilibrio."
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # COLUMNA DERECHA: lectura de las trayectorias.
                    html.Section(
                        className="lv-ana-columna lv-ana-columna-derecha",
                        children=[
                            html.H3("Interpretación de las trayectorias"),
                            html.Section(
                                className="lv-ana-trayectoria",
                                children=[
                                    html.H4("Solución estacionaria"),
                                    formula(
                                        r"Si $(x_0,y_0)=E_*$, entonces "
                                        r"$(x(t),y(t))=E_*$ para todo $t$.",
                                        "lv-ana-texto-matematico",
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-ana-trayectoria",
                                children=[
                                    html.H4("Oscilaciones y plano de fases"),
                                    formula(
                                        r"Las soluciones positivas no estacionarias "
                                        r"describen órbitas cerradas alrededor de $E_*$. "
                                        r"Los máximos de zorros siguen a los de conejos.",
                                        "lv-ana-texto-matematico",
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-ana-trayectoria lv-ana-integral",
                                children=[
                                    html.H4("Integral primera"),
                                    formula(
                                        r"$H(x,y)=\delta x-\gamma\ln x+\beta y-\alpha\ln y$",
                                        "lv-ana-texto-matematico lv-ana-expresion-integral",
                                    ),
                                    formula(
                                        r"Para $x,y>0$, se conserva: "
                                        r"$\frac{dH}{dt}=0$.",
                                        "lv-ana-texto-matematico",
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-ana-idea-clave",
                                children=[
                                    html.Span(
                                        "IDEA CLAVE", className="lv-ana-idea-etiqueta"
                                    ),
                                    html.H4("Oscilar no significa converger."),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
