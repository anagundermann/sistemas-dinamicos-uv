"""Definiciones y propiedades de Sistemas Dinamicos UV."""

CONCEPTOS = {
    "sistema": {
        "titulo": "Sistema dinámico",
        "definicion_texto": (
            "Un sistema dinámico continuo autónomo describe "
            "la evolución de un vector de estado mediante "
            "una ecuación diferencial."
        ),
        "formula": (
            r"\frac{d\mathbf{x}(t)}{dt}"
            r"=F(\mathbf{x}(t);\mathbf{p})"
        ),
        "notacion": (
            r"- $t$: tiempo."
            "\n"
            r"- $\mathbf{x}(t)$: vector de estado."
            "\n"
            r"- $\frac{d\mathbf{x}(t)}{dt}$: derivada temporal del estado."
            "\n"
            r"- $F$: campo vectorial."
            "\n"
            r"- $\mathbf{p}$: vector de parámetros fijos."
        ),
        "explicacion": (
            "Es una regla matemática que describe cómo "
            "evoluciona un sistema con el tiempo, "
            "a partir de su estado y sus parámetros."
        ),
        "propiedades": (
            "En un sistema autónomo, el campo vectorial "
            "no depende explícitamente del tiempo. "
            "Si F es localmente Lipschitz respecto del estado, "
            "cada condición inicial determina una única "
            "solución local para parámetros fijos."
        ),
    },
    "estado": {
        "titulo": "Variable de estado",
        "definicion_texto": (
            "El vector de estado reúne las variables "
            "que describen el sistema en un instante."
        ),
        "formula": (
            r"\mathbf{x}(t)"
            r"=(x_1(t),\ldots,x_n(t))"
        ),
        "notacion": (
            r"- $t$: tiempo."
            "\n"
            r"- $\mathbf{x}(t)$: vector de estado."
            "\n"
            r"- $x_i(t)$: componente $i$ del estado."
            "\n"
            r"- $n$: número de variables de estado."
        ),
        "explicacion": (
            "Es el conjunto de valores que necesitamos "
            "conocer para describir la situación "
            "del sistema en un momento determinado."
        ),
        "propiedades": (
            "Si el vector de estado tiene n componentes, "
            "el espacio de estados es un subconjunto "
            "de ℝⁿ. Una trayectoria describe cómo "
            "evoluciona el estado dentro de ese espacio."
        ),
    },
    "parametro": {
        "titulo": "Parámetro",
        "definicion_texto": (
            "Un parámetro es una cantidad que caracteriza "
            "la ley de evolución del sistema y se considera "
            "fija para cada elección del modelo."
        ),
        "formula": (
            r"\dot{\mathbf{x}}"
            r"=F(\mathbf{x};\mathbf{p})"
        ),
        "notacion": (
            r"- $\mathbf{x}$: vector de estado."
            "\n"
            r"- $\dot{\mathbf{x}}$: derivada temporal del estado."
            "\n"
            r"- $F$: campo vectorial."
            "\n"
            r"- $\mathbf{p}$: vector de parámetros, "
            r"por ejemplo $\alpha,\beta,\gamma$."
        ),
        "explicacion": (
            "Es un valor que forma parte del modelo. "
            "Al modificarlo, puede cambiar la forma "
            "en que evoluciona el sistema."
        ),
        "propiedades": (
            "Para cada valor fijo del vector de parámetros "
            "se obtiene un campo vectorial determinado. "
            "Cambiar los parámetros puede modificar los "
            "equilibrios y la estabilidad del sistema."
        ),
    },
    "condicion_inicial": {
        "titulo": "Condición inicial",
        "definicion_texto": (
            "Es el valor que toma el vector de estado en un instante inicial dado."
        ),
        "formula": (r"\mathbf{x}(t_0)=\mathbf{x}_0"),
        "notacion": (
            r"- $t_0$: instante inicial."
            "\n"
            r"- $\mathbf{x}(t_0)$: estado en ese instante."
            "\n"
            r"- $\mathbf{x}_0$: vector de estado inicial."
        ),
        "explicacion": (
            "Indica el punto desde el cual comienza la evolución del sistema."
        ),
        "propiedades": (
            "Si el campo vectorial es localmente Lipschitz "
            "respecto del estado, el problema de valor "
            "inicial tiene una solución local única. "
            "Esta propiedad no garantiza por sí sola "
            "que la solución exista para todo tiempo."
        ),
    },
    "trayectoria": {
        "titulo": "Trayectoria",
        "definicion_texto": (
            "Una trayectoria describe la evolución "
            "del vector de estado a lo largo del tiempo "
            "mediante una solución del sistema."
        ),
        "formula": (r"t\longmapsto\mathbf{x}(t)"),
        "notacion": (
            r"- $t$: tiempo."
            "\n"
            r"- $\mathbf{x}(t)$: estado en el instante $t$."
            "\n"
            r"- $\longmapsto$: asigna a cada instante "
            r"su estado correspondiente."
        ),
        "explicacion": (
            "Es el recorrido que realiza el estado "
            "del sistema conforme transcurre el tiempo."
        ),
        "propiedades": (
            "Una solución clásica es diferenciable "
            "y satisface la ecuación diferencial "
            "en cada instante de su intervalo de definición. "
            "La trayectoria puede ser constante "
            "cuando corresponde a un equilibrio."
        ),
    },
    "equilibrio": {
        "titulo": "Punto de equilibrio",
        "definicion_texto": (
            "Un punto de equilibrio es un estado "
            "en el cual el campo vectorial se anula."
        ),
        "formula": (
            r"F(\mathbf{x}^{*};\mathbf{p})"
            r"=\mathbf{0}"
        ),
        "notacion": (
            r"- $F$: campo vectorial."
            "\n"
            r"- $\mathbf{x}^{*}$: estado de equilibrio."
            "\n"
            r"- $\mathbf{p}$: vector de parámetros fijos."
            "\n"
            r"- $\mathbf{0}$: vector nulo."
        ),
        "explicacion": (
            "Es un estado en el que el sistema "
            "puede permanecer sin cambiar "
            "a lo largo del tiempo."
        ),
        "propiedades": (
            "Un punto de equilibrio determina una "
            "solución constante. Sin embargo, "
            "la existencia de un equilibrio no implica "
            "que este sea estable. La estabilidad "
            "requiere un análisis adicional."
        ),
    },
    # --------------------------------------------------
    # CONCEPTOS ADICIONALES (BIBLIOTECA MATEMATICA)
    # --------------------------------------------------
    "ecuacion_diferencial": {
        "titulo": "Ecuación diferencial",
        "definicion_texto": (
            "Una ecuación diferencial relaciona una función desconocida "
            "con sus derivadas. En un sistema dinámico continuo, "
            "describe la evolución temporal del vector de estado."
        ),
        "formula": (
            r"\frac{d\mathbf{x}(t)}{dt}"
            r"=F(t,\mathbf{x}(t);\mathbf{p})"
        ),
        "notacion": (
            r"- $t$: tiempo."
            "\n"
            r"- $\mathbf{x}(t)$: vector de estado."
            "\n"
            r"- $\frac{d\mathbf{x}(t)}{dt}$: tasa de cambio del estado."
            "\n"
            r"- $F$: función que determina su evolución."
            "\n"
            r"- $\mathbf{p}$: vector de parámetros del modelo."
        ),
        "explicacion": (
            "Indica cómo cambia el estado en cada instante. "
            "Resolverla permite conocer su evolución a partir "
            "de una condición inicial."
        ),
        "propiedades": (
            "Si F no depende explícitamente del tiempo, "
            "la ecuación es autónoma. Una ecuación diferencial "
            "de orden superior puede expresarse como un sistema "
            "de primer orden al introducir nuevas variables de estado."
        ),
    },
    "espacio_estados": {
        "titulo": "Espacio de estados",
        "definicion_texto": (
            "Es el conjunto de los estados admisibles de un modelo. "
            "Cada punto de ese conjunto representa una posible "
            "configuración del sistema."
        ),
        "formula": (r"\mathbf{x}(t)\in\mathcal{X}\subseteq\mathbb{R}^{n}"),
        "notacion": (
            r"- $\mathbf{x}(t)$: estado del sistema en el instante $t$."
            "\n"
            r"- $\mathcal{X}$: conjunto de estados admisibles."
            "\n"
            r"- $\mathbb{R}^{n}$: espacio de vectores reales de $n$ componentes."
            "\n"
            r"- $n$: número de variables de estado."
        ),
        "explicacion": (
            "Es el espacio donde se representan los estados "
            "y por el que se desplazan las trayectorias del sistema."
        ),
        "propiedades": (
            "El espacio de estados puede estar restringido "
            "por condiciones del modelo. Por ejemplo, "
            "el volumen de líquido en un recipiente de capacidad V "
            "debe estar entre 0 y V."
        ),
    },
    "estabilidad": {
        "titulo": "Estabilidad",
        "definicion_texto": (
            "Un punto de equilibrio es estable en el sentido de Lyapunov "
            "si, para toda distancia positiva al equilibrio, "
            "existe una distancia inicial suficientemente pequeña "
            "que garantiza que las soluciones permanezcan "
            "dentro de la primera para todo tiempo futuro."
        ),
        "formula": (
            r"\|\mathbf{x}(t_0)-\mathbf{x}^{*}\|<\delta"
            r"\;\Longrightarrow\;"
            r"\|\mathbf{x}(t)-\mathbf{x}^{*}\|<\varepsilon"
        ),
        "notacion": (
            r"- $\mathbf{x}^{*}$: punto de equilibrio."
            "\n"
            r"- $\mathbf{x}(t_0)$: estado inicial."
            "\n"
            r"- $\delta>0$: distancia inicial permitida."
            "\n"
            r"- $\varepsilon>0$: distancia máxima exigida para $t\geq t_0$."
        ),
        "explicacion": (
            "Una pequeña perturbación del equilibrio "
            "no provoca que las trayectorias se alejen "
            "arbitrariamente de él."
        ),
        "propiedades": (
            "Ser estable no significa necesariamente que las "
            "trayectorias regresen al equilibrio. "
            "Si el equilibrio es estable y además las soluciones "
            "que comienzan suficientemente cerca convergen a él, "
            "se denomina asintóticamente estable."
        ),
    },
    "plano_fases": {
        "titulo": "Plano de fases",
        "definicion_texto": (
            "Es una representación de la evolución del sistema "
            "en un plano cuyos ejes corresponden a dos "
            "variables de estado, sin usar el tiempo como eje."
        ),
        "formula": (r"t\longmapsto(x_1(t),x_2(t))"),
        "notacion": (
            r"- $t$: tiempo que parametriza la trayectoria."
            "\n"
            r"- $x_1(t)$: primera variable representada."
            "\n"
            r"- $x_2(t)$: segunda variable representada."
            "\n"
            r"- $(x_1(t),x_2(t))$: punto dibujado en el plano."
        ),
        "explicacion": (
            "Permite observar cómo se relacionan dos variables "
            "mientras el sistema evoluciona. Por ejemplo, "
            "pueden representarse las concentraciones de dos reactivos."
        ),
        "propiedades": (
            "En un sistema de dos variables, el plano de fases "
            "representa sus trayectorias en el espacio de estados. "
            "Si el sistema tiene más de dos variables, "
            "la gráfica de dos de ellas es una proyección. "
            "El sentido de recorrido puede indicarse con flechas."
        ),
    },
}
