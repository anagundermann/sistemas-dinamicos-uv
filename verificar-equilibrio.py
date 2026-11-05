from models.modelo_lotka_volterra import simular_lotka_volterra

alpha = 0.5
beta = 0.025
gamma = 0.5
delta = 0.025

x0 = 20
y0 = 20

tiempos, presas, depredadores = simular_lotka_volterra(
    alpha, beta, gamma, delta, x0, y0
)

print("RESULTADOS DE LA SIMULACION")
print("----------------------------")

for i in [0, len(tiempos) // 2, len(tiempos) - 1]:
    print(
        f"t = {tiempos[i]:.2f} | "
        f"Presas = {presas[i]:.12f} | "
        f"Depredadores = {depredadores[i]:.12f}"
    )

error_x = max(abs(x - 20) for x in presas)
error_y = max(abs(y - 20) for y in depredadores)

print("\nERROR MAXIMO RESPECTO AL EQUILIBRIO")
print(f"Presas:       {error_x:.3e}")
print(f"Depredadores: {error_y:.3e}")
