"""Instala Ecosistema conservando el CSS y los graficos de la pagina actual.

Ejecutar UNA VEZ desde la raiz del proyecto: python instalar_ecosistema.py
No sobreescribe pages/depredador_presa.py con una version anterior: hace
reemplazos localizados y crea respaldo al lado de la carpeta del proyecto.
"""

from pathlib import Path
import re
import shutil


raiz = Path(__file__).resolve().parent
pagina = raiz / "pages" / "depredador_presa.py"
modulo = raiz / "components" / "ecosistema_lv.py"
estilos = raiz / "assets" / "zz-ecosistema-lv.css"

if not (pagina.exists() and modulo.exists() and estilos.exists()):
    raise SystemExit("Faltan archivos: extrae todo el ZIP en la raiz de sistemas-dinamicos-uv.")

original = pagina.read_text(encoding="utf-8-sig")
if "from components.ecosistema_lv import crear_contenido_ecosistema" in original:
    raise SystemExit("Ecosistema ya parece instalado. No se ha cambiado nada.")

# La pagina actual ya cuenta con tres botones y un modal compartido.
# Reutilizamos su callback de abrir/cerrar; no creamos otro.
patron_boton = r'(dbc\.Button\(\s*)"Ver modelo"(\s*,\s*id\s*=\s*"lv-boton-modelo")'
patron_modelo = r'(?ms)^    if seccion == "modelo":\s*\n.*?(?=^    if seccion == "ecuaciones":)'
patron_modal = r'(id="lv-modal-informacion",(?:(?!\bchildren=).)*?\bsize=)"lg"'

for etiqueta, patron in [("boton Ver modelo", patron_boton), ("rama modelo", patron_modelo), ("tamano del modal", patron_modal)]:
    if len(list(re.finditer(patron, original, flags=re.DOTALL if etiqueta != "rama modelo" else 0))) != 1:
        raise SystemExit(f"No se pudo identificar de forma segura {etiqueta}. Sin cambios. Enviame tu pages/depredador_presa.py actual.")

if "from models.modelo_lotka_volterra import (" not in original:
    raise SystemExit("No se encontro el bloque de importaciones esperado. Sin cambios.")

cambiado = original.replace(
    "from models.modelo_lotka_volterra import (",
    "from components.ecosistema_lv import crear_contenido_ecosistema\n\nfrom models.modelo_lotka_volterra import (",
    1,
)
cambiado = re.sub(patron_boton, r'\g<1>"Ecosistema"\g<2>', cambiado, count=1)
cambiado = re.sub(
    patron_modelo,
    '    if seccion == "modelo":\n        return "Ecosistema · Zorros y conejos", crear_contenido_ecosistema()\n',
    cambiado,
    count=1,
)
cambiado = re.sub(patron_modal, r'\g<1>"xl"', cambiado, count=1, flags=re.DOTALL)
compile(cambiado, str(pagina), "exec")

respaldo = raiz.parent / "depredador_presa_respaldo_antes_ecosistema.py"
numero = 1
while respaldo.exists():
    respaldo = raiz.parent / f"depredador_presa_respaldo_antes_ecosistema_{numero}.py"
    numero += 1
shutil.copy2(pagina, respaldo)
pagina.write_text(cambiado, encoding="utf-8")
print("Ecosistema instalado correctamente.")
print("Copia del Python anterior:", respaldo)
print("No se alteraron las reglas CSS existentes ni los graficos.")
