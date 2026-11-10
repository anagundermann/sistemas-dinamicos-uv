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


def crear_contenido_analisis_logistico(alpha, beta, gamma, delta, k):
    """Equilibrios y estabilidad local del modelo logistico actual.

    x' = alpha*x*(1 - x/K) - beta*x*y
    y' = delta*x*y - gamma*y

    El caso limite delta*K = gamma se distingue de los hiperbolicos.
    """
    alpha, beta, gamma, delta, k = map(float, (alpha, beta, gamma, delta, k))
    if min(alpha, beta, gamma, delta, k) <= 0:
        raise ValueError("Los parametros del modelo deben ser positivos.")

    x_critico = gamma / delta
    coexistencia = k > x_critico
    umbral = abs(delta * k - gamma) <= 1e-10

    if coexistencia:
        x_estrella = x_critico
        y_estrella = alpha / beta * (1.0 - x_estrella / k)
        traza = -alpha * x_estrella / k
        determinante = alpha * gamma * (1.0 - x_estrella / k)
        discriminante = traza**2 - 4.0 * determinante
        tolerancia = 1e-9 * max(1.0, abs(traza**2), abs(4.0 * determinante))

        if discriminante > tolerancia:
            tipo_estabilidad = "Nodo estable"
            lectura_oscilaciones = (
                "Cerca del equilibrio las soluciones convergen sin oscilar; "
                "la trayectoria no forma una órbita periódica."
            )
        elif discriminante < -tolerancia:
            tipo_estabilidad = "Foco estable"
            lectura_oscilaciones = (
                "Las soluciones próximas pueden oscilar con amplitud decreciente "
                "mientras se acercan al equilibrio."
            )
        else:
            tipo_estabilidad = "Nodo estable (caso límite)"
            lectura_oscilaciones = (
                "Los autovalores reales coinciden; las trayectorias "
                "próximas convergen al equilibrio."
            )

        estado_frontera = "Punto de silla (inestable)"
        descripcion_frontera = "Los depredadores pueden invadir si se introducen."
        estado_coexistencia = tipo_estabilidad + " · asintótico"
        descripcion_coexistencia = (
            f"Con estos parámetros: x* = {x_estrella:.1f}, y* = {y_estrella:.1f}."
        )
        titulo_estabilidad = "Estabilidad de coexistencia"
        bloque_estabilidad = [
            formula(
                r"$\operatorname{tr}J_*=-\frac{\alpha x_*}{K}<0,"
                r"\qquad \det J_*=\alpha\gamma\left(1-\frac{x_*}{K}\right)>0$",
                "lv-ana-formula-autovalores",
            ),
            html.Div(
                className="lv-ana-estabilidad-definiciones",
                children=[
                    html.Div(
                        children=[
                            html.Strong(tipo_estabilidad),
                            html.P(f"Discriminante: {discriminante:.3f}."),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Strong("Asintóticamente estable"),
                            html.P("Las soluciones próximas se acercan a E*."),
                        ],
                    ),
                ],
            ),
            formula(
                r"El origen $E_0=(0,0)$ es un punto de silla (inestable).",
                "lv-ana-descripcion-equilibrio",
            ),
        ]
        solucion_estacionaria = (
            r"Si $(x_0,y_0)=E_*$, entonces "
            r"$(x(t),y(t))=E_*$ para todo $t$."
        )
        idea_clave = "Recursos limitados: el equilibrio atrae trayectorias."
    else:
        if umbral:
            estado_frontera = "Umbral: no hiperbólico"
            descripcion_frontera = (
                "En δK = γ, la linealización tiene un autovalor cero."
            )
        else:
            estado_frontera = "Asintóticamente estable"
            descripcion_frontera = "Los depredadores tienden a desaparecer."
        estado_coexistencia = "No existe coexistencia positiva"
        descripcion_coexistencia = (
            f"Se requiere K > γ/δ = {x_critico:.1f}; actualmente K = {k:g}."
        )
        titulo_estabilidad = "Estabilidad sin coexistencia"
        bloque_estabilidad = [
            formula(
                r"$E_0=(0,0):\quad \lambda_1=\alpha>0,\;"
                r"\lambda_2=-\gamma<0$",
                "lv-ana-formula-autovalores",
            ),
            html.Div(
                className="lv-ana-estabilidad-definiciones",
                children=[
                    html.Div(
                        children=[
                            html.Strong("Origen E0"),
                            html.P("Punto de silla: inestable."),
                        ],
                    ),
                    html.Div(
                        children=[
                            html.Strong("Equilibrio EK"),
                            html.P(
                                "Si K < γ/δ, es asintóticamente estable. "
                                "En el umbral, es no hiperbólico."
                            ),
                        ],
                    ),
                ],
            ),
        ]
        solucion_estacionaria = (
            r"Si $(x_0,y_0)=E_K=(K,0)$, entonces "
            r"$(x(t),y(t))=E_K$ para todo $t$."
        )
        lectura_oscilaciones = (
            "No hay equilibrio positivo de coexistencia. "
            "Con poblaciones iniciales positivas, los depredadores "
            "tienden a cero y las presas a K."
        )
        idea_clave = "Sin coexistencia: presas a K y depredadores a cero."

    return html.Div(
        className="lv-ana lv-ana-compacto",
        children=[
            html.Div(
                className="lv-ana-columnas",
                children=[
                    html.Section(
                        className="lv-ana-columna lv-ana-columna-izquierda",
                        children=[
                            html.H3("Puntos de equilibrio"),
                            html.Div(
                                className="lv-ana-equilibrios",
                                children=[
                                    crear_equilibrio(
                                        "extincion",
                                        "Sin depredadores",
                                        rf"$E_K=({k:g},0)$",
                                        descripcion_frontera,
                                        estado_frontera,
                                    ),
                                    crear_equilibrio(
                                        "coexistencia",
                                        "Coexistencia",
                                        (
                                            r"$x_* = \frac{\gamma}{\delta},\quad "
                                            r"y_* = \frac{\alpha}{\beta}"
                                            r"\left(1-\frac{x_*}{K}\right)$"
                                        ),
                                        descripcion_coexistencia,
                                        estado_coexistencia,
                                    ),
                                ],
                            ),
                            html.H3(
                                titulo_estabilidad,
                                className="lv-ana-titulo-estabilidad",
                            ),
                            html.Section(
                                className="lv-ana-estabilidad-centro",
                                children=bloque_estabilidad,
                            ),
                        ],
                    ),
                    html.Section(
                        className="lv-ana-columna lv-ana-columna-derecha",
                        children=[
                            html.H3("Interpretación de las trayectorias"),
                            html.Section(
                                className="lv-ana-trayectoria",
                                children=[
                                    html.H4("Solución estacionaria"),
                                    formula(
                                        solucion_estacionaria,
                                        "lv-ana-texto-matematico",
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-ana-trayectoria",
                                children=[
                                    html.H4("Oscilaciones y convergencia"),
                                    html.P(
                                        lectura_oscilaciones,
                                        className="lv-ana-texto-matematico",
                                    ),
                                ],
                            ),
                            html.Section(
                                className="lv-ana-trayectoria lv-ana-integral",
                                children=[
                                    html.H4("Ausencia de órbitas cerradas"),
                                    formula(
                                        r"En $x,y>0$, con $B=1/(xy)$: "
                                        r"$\nabla\cdot(BF)=-\alpha/(Ky)<0$. "
                                        r"El criterio de Bendixson-Dulac excluye "
                                        r"las órbitas periódicas.",
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
                                    html.H4(idea_clave),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def crear_contenido_analisis_sistema(
    modelo="clasico", alpha=0.65, beta=0.018, gamma=0.55, delta=0.012, k=120
):
    """Modal compartido: conserva el clasico y adapta el analisis al logistico."""
    if modelo == "logistico":
        return crear_contenido_analisis_logistico(alpha, beta, gamma, delta, k)

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
