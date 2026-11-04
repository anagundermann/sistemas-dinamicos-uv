"""Definiciones consultables de Sistemas Dinamicos UV."""

CONCEPTOS = {
    "sistema": {
        "titulo": "Sistema dinámico",
        "definicion": (
            r"$$\dot{\mathbf{x}}(t)"
            r"=F(\mathbf{x}(t);\mathbf{p})$$"
        ),
        "explicacion": (
            "Un sistema dinámico describe cómo cambia un estado "
            "con el tiempo según una regla de evolución y, "
            "cuando corresponda, ciertos parámetros."
        ),
    },
    "estado": {
        "titulo": "Variable de estado",
        "definicion": (
            r"$$\mathbf{x}(t)"
            r"=(x_1(t),\ldots,x_n(t))$$"
        ),
        "explicacion": (
            "El vector de estado reúne las variables necesarias "
            "para describir la situación del sistema en un instante."
        ),
    },
    "parametro": {
        "titulo": "Parámetro",
        "definicion": (
            r"$$\dot{\mathbf{x}}"
            r"=F(\mathbf{x};\mathbf{p})$$"
        ),
        "explicacion": (
            "Un parámetro caracteriza el modelo, por ejemplo una "
            "tasa de crecimiento o una constante física. "
            "Normalmente se mantiene fijo en cada simulación."
        ),
    },
    "condicion_inicial": {
        "titulo": "Condición inicial",
        "definicion": (r"$$\mathbf{x}(t_0)=\mathbf{x}_0$$"),
        "explicacion": (
            "Indica desde qué estado comienza la evolución "
            "del sistema. Cambiarla puede producir "
            "una trayectoria diferente."
        ),
    },
    "trayectoria": {
        "titulo": "Trayectoria",
        "definicion": (r"$$t\longmapsto\mathbf{x}(t)$$"),
        "explicacion": (
            "Es el recorrido de los estados que adopta "
            "el sistema a lo largo del tiempo."
        ),
    },
    "equilibrio": {
        "titulo": "Punto de equilibrio",
        "definicion": (r"$$F(\mathbf{x}^{*};\mathbf{p})=0$$"),
        "explicacion": (
            "Es un estado en el que el sistema no cambia "
            "con el tiempo si comienza exactamente allí."
        ),
    },
}
