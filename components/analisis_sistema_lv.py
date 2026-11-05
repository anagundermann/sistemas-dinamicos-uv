"""Contenido compacto del modal «Análisis del sistema · Lotka–Volterra».

Mantiene la interfaz acordada: puntos de equilibrio y estabilidad a la
izquierda; interpretación de trayectorias e idea clave a la derecha.
No añade callbacks ni altera los gráficos o el modelo matemático.

La clasificación de estabilidad corresponde al Lotka–Volterra clásico,
con alpha, beta, gamma y delta estrictamente positivos.
"""

from dash import dcc, html


def formula(texto, clase=""):
    """Renderiza LaTeX, incluido el utilizado dentro de frases."""
    return dcc.Markdown(texto, mathjax=True, className=clase)


def crear_equilibrio(tipo, titulo, expresion, descripcion, estabilidad):
    """Muestra cada equilibrio junto con su clasificación, sin repeticiones."""
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
    """Construye la ventana de análisis en dos columnas compactas."""
    return html.Div(
        className="lv-ana",
        children=[
            html.Div(
                className="lv-ana-columnas",
                children=[
                    # COLUMNA IZQUIERDA: equilibrios y valores propios.
                    html.Section(
                        className="lv-ana-columna",
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
                                        r"$E_* = \left(\frac{\gamma}{\delta},\frac{\alpha}{\beta}\right)$",
                                        "Centro estable",
                                        "No asintótico",
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
                                    html.P(
                                        "Las soluciones cercanas oscilan sin converger al equilibrio."
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # COLUMNA DERECHA: interpretación de los gráficos.
                    html.Section(
                        className="lv-ana-columna",
                        children=[
                            html.H3("Interpretación de las trayectorias"),
                            html.Section(
                                className="lv-ana-trayectoria",
                                children=[
                                    html.H4("Evolución temporal"),
                                    html.P(
                                        "Las poblaciones oscilan; los máximos de zorros "
                                        "ocurren después de los de conejos."
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-ana-trayectoria",
                                children=[
                                    html.H4("Plano de fases"),
                                    formula(
                                        r"Las trayectorias positivas no estacionarias "
                                        r"forman órbitas cerradas alrededor de $E_*$. ",
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
                                    html.P(
                                        "Las oscilaciones no se amortiguan en el modelo clásico."
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
