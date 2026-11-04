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
}
