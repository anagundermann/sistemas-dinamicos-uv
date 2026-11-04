"""Modelo clasico de Lotka-Volterra (presas y depredadores)."""

import numpy as np
from scipy.integrate import solve_ivp


def calcular_equilibrio(alpha, beta, gamma, delta):
    """Retorna el equilibrio de coexistencia (presas, depredadores)."""
    return gamma / delta, alpha / beta


def simular_lotka_volterra(
    alpha,
    beta,
    gamma,
    delta,
    presas_iniciales,
    depredadores_iniciales,
    duracion=40.0,
    puntos=801,
):
    """Resuelve las dos ecuaciones diferenciales del modelo."""

    if min(alpha, beta, gamma, delta) <= 0:
        raise ValueError("Los parametros deben ser positivos.")

    if min(presas_iniciales, depredadores_iniciales) <= 0:
        raise ValueError("Las poblaciones iniciales deben ser positivas.")

    def ecuaciones(_t, estado):
        presas, depredadores = estado

        return [
            alpha * presas - beta * presas * depredadores,
            delta * presas * depredadores - gamma * depredadores,
        ]

    tiempos = np.linspace(0.0, duracion, puntos)

    solucion = solve_ivp(
        ecuaciones,
        (0.0, duracion),
        [presas_iniciales, depredadores_iniciales],
        t_eval=tiempos,
        rtol=1e-8,
        atol=1e-10,
    )

    if not solucion.success:
        raise RuntimeError(solucion.message)

    return solucion.t, solucion.y[0], solucion.y[1]
