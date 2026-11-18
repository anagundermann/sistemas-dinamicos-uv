"""Referencia teorica de equilibrios y estabilidad de Lotka-Volterra.

Separa las condiciones de equilibrio de su clasificacion local en dos
pestanas. No utiliza resultados de los sliders; esos corresponden al
analisis de la dinamica. No altera la integracion ni otros laboratorios.
"""

from dash import dcc, html


def formula(texto, clase=""):
    """Renderiza expresiones LaTeX con MathJax."""
    clases = "lv-ana-teoria-formula"
    if clase:
        clases += f" {clase}"
    return dcc.Markdown(texto, mathjax=True, className=clases)


def tarjeta(titulo, contenido, clase=""):
    """Tarjeta teorica compacta, con estilos locales al modal."""
    clases = "lv-ana-teoria-tarjeta"
    if clase:
        clases += f" {clase}"
    return html.Section(
        className=clases,
        children=[html.H4(titulo), *contenido],
    )


def idea_clave(texto):
    return html.Section(
        className="lv-ana-idea-clave lv-ana-teoria-idea",
        children=[
            html.Span("IDEA CLAVE", className="lv-ana-idea-etiqueta"),
            html.P(texto),
        ],
    )


def pestana_equilibrios_logistico():
    return html.Div(
        className="lv-ana-teoria-contenido",
        children=[
            html.Div(
                className="lv-ana-teoria-columnas",
                children=[
                    html.Section(
                        className="lv-ana-teoria-columna",
                        children=[
                            html.H3("Equilibrios de frontera"),
                            tarjeta(
                                "Origen · Extinción total",
                                [
                                    formula(r"$$E_0=(0,0)$$"),
                                    html.P("No hay presas ni depredadores."),
                                ],
                            ),
                            tarjeta(
                                "Sin depredadores",
                                [
                                    formula(r"$$E_K=(K,0)$$"),
                                    html.P(
                                        "Las presas alcanzan la capacidad de carga K."
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Section(
                        className="lv-ana-teoria-columna",
                        children=[
                            html.H3("Coexistencia positiva"),
                            tarjeta(
                                "Ambas poblaciones presentes",
                                [
                                    formula(r"$$x_*=\frac{\gamma}{\delta}$$"),
                                    formula(
                                        r"$$y_*=\frac{\alpha}{\beta}"
                                        r"\left(1-\frac{\gamma}{\delta K}\right)$$"
                                    ),
                                    html.Div(
                                        className="lv-ana-teoria-condicion",
                                        children=[
                                            html.Strong("Condición de existencia"),
                                            formula(r"$$K>\frac{\gamma}{\delta}$$"),
                                        ],
                                    ),
                                    html.P(
                                        "Si K = γ/δ, la coexistencia coincide "
                                        "con Eₖ y no es estrictamente positiva. "
                                        "Si K < γ/δ, no hay coexistencia positiva."
                                    ),
                                ],
                                "lv-ana-teoria-verde",
                            ),
                        ],
                    ),
                ],
            ),
            idea_clave(
                "Un equilibrio satisface x′ = 0 e y′ = 0. "
                "La existencia de coexistencia positiva depende de K; "
                "la estabilidad se estudia en la segunda pestaña."
            ),
        ],
    )


def pestana_equilibrios_clasico():
    return html.Div(
        className="lv-ana-teoria-contenido",
        children=[
            html.Div(
                className="lv-ana-teoria-columnas",
                children=[
                    html.Section(
                        className="lv-ana-teoria-columna",
                        children=[
                            html.H3("Puntos de equilibrio"),
                            tarjeta(
                                "Origen · Extinción total",
                                [
                                    formula(r"$$E_0=(0,0)$$"),
                                    html.P("Ambas poblaciones son nulas."),
                                ],
                            ),
                            tarjeta(
                                "Coexistencia",
                                [
                                    formula(
                                        r"$$E_*=\left(\frac{\gamma}{\delta},"
                                        r"\frac{\alpha}{\beta}\right)$$"
                                    ),
                                    html.P("Las dos poblaciones son positivas."),
                                ],
                                "lv-ana-teoria-verde",
                            ),
                        ],
                    ),
                    html.Section(
                        className="lv-ana-teoria-columna",
                        children=[
                            html.H3("Condiciones y significado"),
                            tarjeta(
                                "Existencia de coexistencia",
                                [
                                    formula(r"$$\alpha,\beta,\gamma,\delta>0$$"),
                                    html.P(
                                        "Con parámetros positivos, E* existe "
                                        "en el primer cuadrante."
                                    ),
                                ],
                            ),
                            tarjeta(
                                "¿Qué es una solución estacionaria?",
                                [
                                    formula(
                                        r"$$F(E)=0\quad\Longrightarrow\quad"
                                        r"(x(t),y(t))=E$$"
                                    ),
                                    html.P(
                                        "Si se inicia exactamente en un equilibrio, "
                                        "las poblaciones permanecen constantes."
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            idea_clave(
                "En el modelo clásico, con parámetros positivos, "
                "existen el origen y un equilibrio de coexistencia. "
                "La segunda pestaña explica su estabilidad."
            ),
        ],
    )


def tarjeta_criterios(texto_idea):
    return html.Section(
        className="lv-ana-teoria-columna",
        children=[
            html.H3("Linealización en un equilibrio"),
            tarjeta(
                "Traza, determinante y autovalores",
                [
                    formula(
                        r"$$J(E)=\begin{pmatrix} f_x & f_y \\ g_x & g_y "
                        r"\end{pmatrix}_{E}$$"
                    ),
                    formula(r"$$T=\operatorname{tr}J(E),\qquad D=\det J(E)$$"),
                    formula(r"$$\Delta=T^2-4D$$"),
                    formula(r"$$\lambda_{\pm}=\frac{T\pm\sqrt{\Delta}}{2}$$"),
                    html.Div(
                        className="lv-ana-teoria-criterios",
                        children=[
                            html.P(
                                [html.Strong("D < 0: "), "punto de silla (inestable)."]
                            ),
                            html.P([html.Strong("D > 0, T < 0: "), "atractor local."]),
                            html.P([html.Strong("D > 0, T > 0: "), "repulsor local."]),
                            html.P(
                                [
                                    html.Strong("D = 0: "),
                                    "linealización no concluyente.",
                                ]
                            ),
                        ],
                    ),
                    html.P(
                        "Con autovalores de parte real nula, "
                        "la linealización puede no decidir la estabilidad.",
                        className="lv-ana-teoria-nota",
                    ),
                ],
                "lv-ana-teoria-crema",
            ),
            # Idea clave inmediatamente bajo la tarjeta de criterios.
            # No ocupa una fila de ancho completo bajo las dos columnas.
            idea_clave(texto_idea),
        ],
    )


def tarjeta_discriminante():
    return tarjeta(
        "Tipo geométrico si D > 0 y T < 0",
        [
            html.Div(
                className="lv-ana-teoria-tipos",
                children=[
                    html.Div(
                        [
                            html.Strong("Δ > 0"),
                            html.Span(
                                "Nodo estable · dos autovalores reales negativos."
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Δ = 0"),
                            html.Span("Autovalor negativo doble · nodo degenerado."),
                        ]
                    ),
                    html.Div(
                        [
                            html.Strong("Δ < 0"),
                            html.Span(
                                "Foco estable · autovalores complejos con parte real negativa."
                            ),
                        ]
                    ),
                ],
            ),
            html.P(
                "El discriminante distingue la forma de la aproximación; "
                "no determina por sí solo la estabilidad.",
                className="lv-ana-teoria-nota",
            ),
        ],
    )


def pestana_estabilidad_logistico():
    return html.Div(
        className="lv-ana-teoria-contenido",
        children=[
            html.Div(
                className="lv-ana-teoria-columnas",
                children=[
                    tarjeta_criterios(
                        "En la coexistencia logística, T* < 0 y D* > 0 "
                        "garantizan estabilidad asintótica; Δ distingue nodo y foco."
                    ),
                    html.Section(
                        className="lv-ana-teoria-columna",
                        children=[
                            html.H3("Clasificación y modelo logístico"),
                            tarjeta_discriminante(),
                            tarjeta(
                                "En la coexistencia positiva",
                                [
                                    formula(
                                        r"$$\begin{aligned}"
                                        r"T_* &= -\frac{\alpha x_*}{K}<0,"
                                        r"\\[5pt]"
                                        r"D_* &= \alpha\gamma\left(1-\frac{x_*}{K}\right)>0"
                                        r"\end{aligned}$$"
                                    ),
                                    html.P(
                                        "E* siempre es asintóticamente estable: "
                                        "nodo o foco según Δ."
                                    ),
                                    html.P(
                                        "E₀ es una silla. En Eₖ los autovalores "
                                        "son −α y δK−γ: estable si K < γ/δ, "
                                        "silla si K > γ/δ; en la igualdad, "
                                        "la linealización es no hiperbólica.",
                                        className="lv-ana-teoria-nota",
                                    ),
                                ],
                                "lv-ana-teoria-verde",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def pestana_estabilidad_clasico():
    return html.Div(
        className="lv-ana-teoria-contenido",
        children=[
            html.Div(
                className="lv-ana-teoria-columnas",
                children=[
                    tarjeta_criterios(
                        "Un centro es estable sin atraer trayectorias. "
                        "No debe confundirse con un foco estable, "
                        "que presenta convergencia en espiral."
                    ),
                    html.Section(
                        className="lv-ana-teoria-columna",
                        children=[
                            html.H3("Clasificación y modelo clásico"),
                            tarjeta_discriminante(),
                            tarjeta(
                                "En el equilibrio de coexistencia",
                                [
                                    formula(
                                        r"$$T_*=0,\quad D_*=\alpha\gamma>0,\quad"
                                        r"\lambda_\pm=\pm i\sqrt{\alpha\gamma}$$"
                                    ),
                                    html.P(
                                        "La linealización tiene un centro; "
                                        "en este sistema, E* es estable, "
                                        "pero no asintóticamente estable."
                                    ),
                                    html.P(
                                        "La integral primera es constante a lo "
                                        "largo de las soluciones positivas:",
                                        className="lv-ana-teoria-nota",
                                    ),
                                    formula(
                                        r"$$H=\delta x-\gamma\ln x+\beta y-\alpha\ln y$$"
                                    ),
                                    html.P(
                                        "Esta conservación justifica las órbitas "
                                        "cerradas alrededor de E*. El origen es una silla.",
                                        className="lv-ana-teoria-nota",
                                    ),
                                ],
                                "lv-ana-teoria-verde",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def crear_contenido_analisis_logistico(alpha, beta, gamma, delta, k):
    """Conserva compatibilidad con la interfaz anterior; contenido teorico."""
    return _crear_modal_teorico("logistico")


def _crear_modal_teorico(modelo, pestana="equilibrios"):
    """Devuelve una sola seccion; los controles estan en la cabecera del modal.

    Esto evita duplicar las pestanas dentro del cuerpo y conserva la altura.
    """
    es_logistico = modelo == "logistico"
    if pestana == "estabilidad":
        contenido = (
            pestana_estabilidad_logistico()
            if es_logistico
            else pestana_estabilidad_clasico()
        )
    else:
        contenido = (
            pestana_equilibrios_logistico()
            if es_logistico
            else pestana_equilibrios_clasico()
        )
    return html.Div(
        className="lv-ana lv-ana-teoria",
        key=f"lv-teoria-{modelo}-{pestana}",
        children=[contenido],
    )


def crear_contenido_analisis_sistema(
    modelo="clasico",
    alpha=0.65,
    beta=0.018,
    gamma=0.55,
    delta=0.012,
    k=120,
    pestana="equilibrios",
):
    """Contenido teorico; la seleccion de pestana viene de la cabecera.

    Conserva la firma compatible con el resto del laboratorio.
    """
    return _crear_modal_teorico(modelo, pestana=pestana)
