"""Modelo depredador-presa con crecimiento logistico de las presas.

    x' = alpha*x*(1 - x/K) - beta*x*y
    y' = delta*x*y - gamma*y

Mantiene la misma malla de tiempo y precision del modelo clasico.
"""

import numpy as np
from scipy.integrate import solve_ivp


def calcular_equilibrio_logistico(alpha, beta, gamma, delta, k):
    """Devuelve (x*, y*) si existe coexistencia positiva; si no, None.

    La coexistencia positiva requiere K > gamma/delta.
    El equilibrio (K, 0) siempre existe para K > 0.
    """
    if min(alpha, beta, gamma, delta, k) <= 0:
        raise ValueError("Los parametros deben ser positivos.")

    presas_eq = gamma / delta
    if k <= presas_eq:
        return None

    depredadores_eq = (alpha / beta) * (1.0 - presas_eq / k)
    return presas_eq, depredadores_eq


def simular_lotka_logistico(
    alpha,
    beta,
    gamma,
    delta,
    presas_iniciales,
    depredadores_iniciales,
    k,
    duracion=40.0,
    puntos=801,
):
    """Integra el modelo logístico con RK45 y devuelve (t, x, y)."""
    if min(alpha, beta, gamma, delta, k) <= 0:
        raise ValueError("Los parametros deben ser positivos.")

    if min(presas_iniciales, depredadores_iniciales) <= 0:
        raise ValueError("Las poblaciones iniciales deben ser positivas.")

    if duracion <= 0 or puntos < 2:
        raise ValueError(
            "La duracion debe ser positiva y debe haber al menos dos puntos."
        )

    def ecuaciones(_t, estado):
        presas, depredadores = estado
        return [
            alpha * presas * (1.0 - presas / k) - beta * presas * depredadores,
            delta * presas * depredadores - gamma * depredadores,
        ]

    tiempos = np.linspace(0.0, duracion, puntos)
    solucion = solve_ivp(
        ecuaciones,
        (0.0, duracion),
        [presas_iniciales, depredadores_iniciales],
        t_eval=tiempos,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )

    if not solucion.success:
        raise RuntimeError(solucion.message)

    return solucion.t, solucion.y[0], solucion.y[1]
