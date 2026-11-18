"""Visita guiada reutilizable para Sistemas Dinamicos UV.

Instalacion posterior en app.py:
    from components.tutorial_guiado import crear_tutorial_guiado, registrar_callbacks_tutorial
    # Anadir crear_tutorial_guiado() una sola vez a los hijos de app.layout.
    # Despues de registrar los callbacks de las paginas:
    registrar_callbacks_tutorial(app)

No modifica las paginas, sus simuladores ni su distribucion.
Requiere assets/zz-tutorial-guiado.css y assets/zz-tutorial-guiado.js.
"""

from dash import Input, Output, State, ctx, dcc, html


# El selector CSS identifica un elemento existente en cada laboratorio.
# Para incorporar otros laboratorios, agregar otra entrada a GUIAS.
GUIAS = {
    "depredador_presa": (
        {
            "titulo": "Experimenta con los parámetros",
            "texto": (
                "Modifica las condiciones del ecosistema y observa cómo "
                "cambia la evolución de presas y depredadores."
            ),
            "objetivo": ".lv-panel-controles",
        },
        {
            "titulo": "Observa las dos representaciones",
            "texto": (
                "Compara la evolución temporal de las poblaciones con el "
                "plano de fases para interpretar su relación."
            ),
            "objetivo": ".lv-panel-graficos",
        },
        {
            "titulo": "Compara los modelos",
            "texto": (
                "Cambia entre el modelo clásico y el de crecimiento "
                "logístico para explorar diferentes comportamientos."
            ),
            "objetivo": ".lv-selector-modelo",
        },
        {
            "titulo": "Analiza la dinámica del sistema",
            "texto": (
                "En «Análisis de la dinámica» puedes estudiar un instante "
                "mediante tasas y variaciones, o la simulación completa "
                "para explorar la estabilidad del equilibrio, las "
                "oscilaciones y su evolución."
            ),
            "objetivo": ".lv-selector-modelo",
        },
        {
            "titulo": "Cambia de laboratorio",
            "texto": (
                "Pulsa la pestaña gris con la flecha del borde derecho "
                "para desplegar los laboratorios y cambiar de modelo "
                "sin volver a Inicio."
            ),
            "objetivo": "",  # Nota final: sin recuadro de resaltado.
        },
    ),
    "sir": (
        {
            "titulo": "Experimenta con los parámetros",
            "texto": (
                "Modifica las tasas de infección, recuperación y transmisión "
                "entre regiones para explorar distintos escenarios epidémicos."
            ),
            "objetivo": ".sir-controles-epidemicos",
        },
        {
            "titulo": "Configura el escenario",
            "texto": (
                "Selecciona dónde comienza el brote, elige la región de análisis "
                "y ajusta el día para observar la evolución del sistema."
            ),
            "objetivo": (
                ".sir-panel-subtitulo, .sir-control-select, #sir-slider-dia-grafo"
            ),
        },
        {
            "titulo": "Explora las representaciones",
            "texto": (
                "Conoce las tres vistas disponibles: curvas S–I–R, grafo "
                "espacial de Chile y matriz espacio-temporal."
            ),
            "objetivo": ".sir-tabs",
        },
        {
            "titulo": "Interpreta los resultados",
            "texto": (
                "Revisa las proporciones de susceptibles, infectados y "
                "recuperados, junto con la lectura del escenario simulado."
            ),
            "objetivo": ".sir-resultados",
        },
        {
            "titulo": "Cambia de laboratorio",
            "texto": (
                "Pulsa la pestaña gris con la flecha del borde derecho "
                "para desplegar los laboratorios y cambiar de modelo "
                "sin volver a Inicio."
            ),
            "objetivo": "",  # Nota final: sin recuadro de resaltado.
        },
    ),
    "pendulo_simple": (
        {
            "titulo": "Controla la simulación",
            "texto": (
                "Iniciar y Reiniciar te permiten observar el movimiento desde "
                "el mismo punto de partida. Las estelas muestran por dónde pasó la masa."
            ),
            "prueba": "Inicia el movimiento unos segundos; luego reinicia a t = 0 y compara.",
            "objetivo": "#ps-panel-simulador .top-controls .action-row",
        },
        {
            "titulo": "El ángulo inicial cambia la oscilación",
            "texto": (
                "θ₁ fija la inclinación de partida. Para ángulos pequeños el "
                "movimiento se aproxima al armónico; para grandes ángulos, no."
            ),
            "prueba": "Compara θ₁ = 15° con θ₁ = 120°; observa si tardan lo mismo en oscilar.",
            "objetivo": "#ps-panel-simulador .sliders-panel > .slider-group:nth-child(1)",
        },
        {
            "titulo": "Longitud y gravedad: cambia el ritmo",
            "texto": (
                "Una longitud mayor tiende a hacer la oscilación más lenta; "
                "una gravedad mayor, más rápida. Compáralas manteniendo el mismo ángulo."
            ),
            "prueba": "Cambia L₁ de 2 a 1 m y observa el ritmo. Después restablece L₁.",
            "objetivo": (
                "#ps-panel-simulador .sliders-panel > .slider-group:nth-child(4), "
                "#ps-panel-simulador .sliders-panel > .slider-group:nth-child(5)"
            ),
        },
        {
            "titulo": "Una sorpresa: la masa no cambia el período",
            "texto": (
                "En este modelo, m₁ no aparece en la ecuación del movimiento: "
                "cambiarla no cambia θ₁(t), aunque sí modifica la energía en joules."
            ),
            "prueba": "Mantén lo demás fijo y cambia m₁ de 1 a 4 kg; compara movimiento y energía.",
            "objetivo": "#ps-panel-simulador .sliders-panel > .slider-group:nth-child(7)",
        },
        {
            "titulo": "Amortiguamiento: ¿a dónde va la energía?",
            "texto": (
                "Con b = 0, la energía ideal se conserva aproximadamente en "
                "la integración numérica. Con b > 0, el movimiento pierde amplitud."
            ),
            "prueba": "Prueba b = 0 y luego b = 0.15; observa el movimiento y la energía E.",
            "objetivo": "#ps-panel-simulador .sliders-panel > .slider-group:nth-child(6)",
        },
        {
            "titulo": "Varios inicios casi iguales",
            "texto": (
                "N muestra varias trayectorias con pequeñas perturbaciones "
                "iniciales Δθ₀. Su separación no implica caos en el péndulo simple."
            ),
            "prueba": "Usa N = 5 y log₁₀(Δθ₀) = −3; compara después con −6.",
            "objetivo": (
                "#ps-panel-simulador .sliders-panel > .slider-group:nth-child(2), "
                "#ps-panel-simulador .sliders-panel > .slider-group:nth-child(3)"
            ),
        },
        {
            "titulo": "Interpreta los dos gráficos",
            "texto": (
                "Arriba se muestra la separación logarítmica entre trayectorias; "
                "abajo, el espacio de fases (ángulo θ₁ frente a velocidad ω₁). "
                "Una espiral hacia el reposo indica disipación."
            ),
            "prueba": "Con b = 0 observa las curvas; aumenta b y busca una espiral que se cierre.",
            "objetivo": "#ps-panel-simulador .right-column",
        },
        {
            "titulo": "Guarda y compara tus experimentos",
            "texto": (
                "En «Mediciones y guía teórica» puedes capturar el estado "
                "actual, examinar la tabla y exportar los resultados a CSV."
            ),
            "prueba": "Investiga qué cambia al variar una sola variable por vez.",
            "objetivo": "#ps-tabs-navigation",
        },
        {
            "titulo": "Cambia de laboratorio",
            "texto": (
                "Pulsa la pestaña gris con la flecha del borde derecho "
                "para desplegar los laboratorios y cambiar de modelo "
                "sin volver a Inicio."
            ),
            "objetivo": "",  # Nota final: sin recuadro de resaltado.
        },
    ),
    "pendulo_doble": (
        {
            "titulo": "Comienza por controlar el movimiento",
            "texto": (
                "Iniciar y Reiniciar permiten comparar ensayos desde t = 0. "
                "Puedes limpiar o fijar las estelas para estudiar las trayectorias."
            ),
            "prueba": "Inicia unos segundos y reinicia; fíjate cómo cambian las estelas.",
            "objetivo": "#pd-panel-simulador .top-controls .action-row",
        },
        {
            "titulo": "Dos ángulos, dos condiciones iniciales",
            "texto": (
                "θ₁ y θ₂ determinan la posición inicial de cada brazo. "
                "Cambios pequeños pueden producir movimientos muy diferentes más adelante."
            ),
            "prueba": "Compara θ₂ = −10° y θ₂ = −9°, sin cambiar los otros parámetros.",
            "objetivo": (
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(1), "
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(2)"
            ),
        },
        {
            "titulo": "Perturbaciones y varias trayectorias",
            "texto": (
                "N permite observar múltiples péndulos dobles. "
                "log₁₀(Δθ₀) controla cuán pequeñas son las diferencias iniciales."
            ),
            "prueba": "Con N = 5, compara perturbaciones −3 y −6: ¿cuánto tardan en separarse?",
            "objetivo": (
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(3), "
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(4)"
            ),
        },
        {
            "titulo": "Cambia la geometría del sistema",
            "texto": (
                "L₁ y L₂ son las longitudes de los dos brazos. Modificar "
                "una sola cambia la geometría y la dinámica de ambos ángulos."
            ),
            "prueba": "Mantén L₁ = 2 m y compara L₂ = 1 m con L₂ = 2 m.",
            "objetivo": (
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(5), "
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(6)"
            ),
        },
        {
            "titulo": "Aquí sí importan las dos masas",
            "texto": (
                "A diferencia del péndulo simple ideal, la relación entre "
                "m₁ y m₂ influye en cómo intercambian movimiento los dos brazos."
            ),
            "prueba": "Compara (m₁, m₂) = (1, 1) kg con (1, 4) kg.",
            "objetivo": (
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(9), "
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(10)"
            ),
        },
        {
            "titulo": "Gravedad y amortiguamiento",
            "texto": (
                "g modifica la acción de la gravedad; b introduce pérdida "
                "de energía. Con amortiguamiento, el sistema tiende a detenerse."
            ),
            "prueba": "Compara b = 0 y b = 0.10 con el mismo g y los mismos ángulos.",
            "objetivo": (
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(7), "
                "#pd-panel-simulador .sliders-panel > .slider-group:nth-child(8)"
            ),
        },
        {
            "titulo": "Observa la trayectoria física",
            "texto": (
                "Cada brazo gira e influye en el otro. Las estelas ayudan "
                "a visualizar la complejidad del movimiento, pero el caos no "
                "se identifica solo porque una figura parezca enredada."
            ),
            "prueba": "Fija estelas y observa dos ensayos con ángulos iniciales casi iguales.",
            "objetivo": "#pd-canvas-physics-host",
        },
        {
            "titulo": "Divergencia y espacio de configuración",
            "texto": (
                "El gráfico superior muestra log₁₀(Δθ); el inferior compara "
                "θ₁ con θ₂. Este último es espacio de configuración, no "
                "un plano de fases completo."
            ),
            "prueba": "Busca separación sostenida entre trayectorias y compárala con el dibujo físico.",
            "objetivo": "#pd-panel-simulador .right-column",
        },
        {
            "titulo": "Registra las observaciones",
            "texto": (
                "La pestaña «Mediciones y guía teórica» permite capturar "
                "el estado del sistema y descargar CSV para comparar ensayos."
            ),
            "prueba": "Cambia solo un parámetro por ensayo y anota cuándo divergen las trayectorias.",
            "objetivo": "#pd-tabs-navigation",
        },
        {
            "titulo": "Cambia de laboratorio",
            "texto": (
                "Pulsa la pestaña gris con la flecha del borde derecho "
                "para desplegar los laboratorios y cambiar de modelo "
                "sin volver a Inicio."
            ),
            "objetivo": "",  # Nota final: sin recuadro de resaltado.
        },
    ),
}

_ESTADO_INICIAL = {"pagina": None, "paso": 0, "abierta": False}


def crear_tutorial_guiado():
    """Devuelve el componente global; debe montarse una sola vez en app.layout."""
    return html.Div(
        id="sd-guia-componente",
        children=[
            dcc.Store(id="sd-guia-estado", data=_ESTADO_INICIAL),
            dcc.Store(id="sd-guia-vistas", data={}, storage_type="memory"),
            dcc.Store(id="sd-guia-escena", data={}),
            dcc.Store(id="sd-guia-sincronizada"),
            html.Button(
                "?",
                id="sd-guia-reabrir",
                n_clicks=0,
                className="sd-guia-ayuda sd-guia-ayuda-oculta",
                type="button",
                title="Volver a ver la guía",
                **{"aria-label": "Volver a ver la guía interactiva"},
            ),
            html.Div(
                id="sd-guia-overlay",
                className="sd-guia sd-guia-oculta",
                children=[
                    html.Button(
                        "",
                        id="sd-guia-fondo",
                        n_clicks=0,
                        className="sd-guia-fondo",
                        type="button",
                        title="Cerrar guía",
                        **{"aria-label": "Cerrar guía interactiva"},
                    ),
                    html.Div(
                        id="sd-guia-resalte",
                        className="sd-guia-resalte",
                        **{"aria-hidden": "true"},
                    ),
                    html.Section(
                        id="sd-guia-tarjeta",
                        className="sd-guia-tarjeta",
                        role="dialog",
                        **{
                            "aria-modal": "true",
                            "aria-label": "Tutorial interactivo del laboratorio",
                            "tabIndex": -1,
                        },
                        children=[
                            html.Div(
                                className="sd-guia-cabecera",
                                children=[
                                    html.Span(
                                        "GUÍA INTERACTIVA",
                                        className="sd-guia-etiqueta",
                                    ),
                                    html.Button(
                                        "×",
                                        id="sd-guia-cerrar",
                                        n_clicks=0,
                                        className="sd-guia-cerrar",
                                        type="button",
                                        title="Cerrar guía",
                                        **{"aria-label": "Cerrar guía"},
                                    ),
                                ],
                            ),
                            html.Span(
                                id="sd-guia-contador", className="sd-guia-contador"
                            ),
                            html.H2(id="sd-guia-titulo", className="sd-guia-titulo"),
                            html.P(id="sd-guia-texto", className="sd-guia-texto"),
                            html.Div(
                                id="sd-guia-experimento",
                                className="sd-guia-experimento sd-guia-experimento-oculto",
                            ),
                            html.Div(
                                id="sd-guia-progreso",
                                className="sd-guia-progreso",
                                **{"aria-label": "Progreso de la guia"},
                            ),
                            html.Div(
                                className="sd-guia-acciones",
                                children=[
                                    html.Button(
                                        "Saltar guía",
                                        id="sd-guia-omitir",
                                        n_clicks=0,
                                        type="button",
                                        className="sd-guia-omitir",
                                    ),
                                    html.Div(
                                        className="sd-guia-navegacion",
                                        children=[
                                            html.Button(
                                                "Anterior",
                                                id="sd-guia-anterior",
                                                n_clicks=0,
                                                type="button",
                                                className="sd-guia-anterior",
                                            ),
                                            html.Button(
                                                "Siguiente →",
                                                id="sd-guia-siguiente",
                                                n_clicks=0,
                                                type="button",
                                                className="sd-guia-siguiente",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def registrar_callbacks_tutorial(app):
    """Registrar una unica vez al configurar la aplicacion Dash."""

    @app.callback(
        Output("sd-guia-estado", "data"),
        Output("sd-guia-vistas", "data"),
        Input("sd-pagina-activa", "data"),
        Input("sd-guia-siguiente", "n_clicks"),
        Input("sd-guia-anterior", "n_clicks"),
        Input("sd-guia-omitir", "n_clicks"),
        Input("sd-guia-cerrar", "n_clicks"),
        Input("sd-guia-fondo", "n_clicks"),
        Input("sd-guia-reabrir", "n_clicks"),
        State("sd-guia-estado", "data"),
        State("sd-guia-vistas", "data"),
    )
    def actualizar_estado_tutorial(
        pagina,
        _siguiente,
        _anterior,
        _omitir,
        _cerrar,
        _fondo,
        _reabrir,
        estado,
        vistas,
    ):
        estado = dict(estado or _ESTADO_INICIAL)
        vistas = dict(vistas or {})
        disparador = ctx.triggered_id
        pasos = GUIAS.get(pagina)

        if not pasos:
            return {"pagina": pagina, "paso": 0, "abierta": False}, vistas

        # La primera visita abre automaticamente la guia. La siguiente no.
        if disparador in (None, "sd-pagina-activa") or estado.get("pagina") != pagina:
            return {
                "pagina": pagina,
                "paso": 0,
                "abierta": not bool(vistas.get(pagina)),
            }, vistas

        if disparador == "sd-guia-reabrir":
            return {"pagina": pagina, "paso": 0, "abierta": True}, vistas

        if not estado.get("abierta"):
            return estado, vistas

        if disparador in ("sd-guia-omitir", "sd-guia-cerrar", "sd-guia-fondo"):
            vistas[pagina] = True
            return {"pagina": pagina, "paso": 0, "abierta": False}, vistas

        actual = max(0, min(int(estado.get("paso", 0)), len(pasos) - 1))

        if disparador == "sd-guia-anterior":
            return {
                "pagina": pagina,
                "paso": max(0, actual - 1),
                "abierta": True,
            }, vistas

        if disparador == "sd-guia-siguiente":
            if actual == len(pasos) - 1:
                vistas[pagina] = True
                return {"pagina": pagina, "paso": 0, "abierta": False}, vistas
            return {"pagina": pagina, "paso": actual + 1, "abierta": True}, vistas

        return estado, vistas

    @app.callback(
        Output("sd-guia-overlay", "className"),
        Output("sd-guia-reabrir", "className"),
        Output("sd-guia-contador", "children"),
        Output("sd-guia-titulo", "children"),
        Output("sd-guia-texto", "children"),
        Output("sd-guia-experimento", "children"),
        Output("sd-guia-experimento", "className"),
        Output("sd-guia-progreso", "children"),
        Output("sd-guia-anterior", "disabled"),
        Output("sd-guia-siguiente", "children"),
        Output("sd-guia-escena", "data"),
        Input("sd-guia-estado", "data"),
    )
    def presentar_tutorial(estado):
        estado = estado or _ESTADO_INICIAL
        pagina = estado.get("pagina")
        pasos = GUIAS.get(pagina, ())
        abierto = bool(estado.get("abierta")) and bool(pasos)
        indice = min(max(int(estado.get("paso", 0)), 0), len(pasos) - 1) if pasos else 0
        paso = pasos[indice] if pasos else {"titulo": "", "texto": "", "objetivo": ""}

        # El último paso usa el mismo simbolo que la pestana lateral,
        # pero solo como referencia visual: no es un boton interactivo.
        texto_paso = paso["texto"]
        if paso["titulo"] == "Cambia de laboratorio":
            simbolo_pestana = html.Span(
                "‹",
                style={
                    "display": "inline-flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "width": "19px",
                    "height": "29px",
                    "borderRadius": "7px",
                    "backgroundColor": "#A9B6C5",
                    "border": "1px solid #91A3B8",
                    "color": "#FFFFFF",
                    "fontSize": "22px",
                    "fontWeight": "600",
                    "lineHeight": "1",
                    "verticalAlign": "middle",
                    "margin": "0 5px",
                },
                **{"aria-hidden": "true"},
            )
            texto_paso = [
                "Para cambiar de laboratorio, pulsa la pestaña gris ",
                simbolo_pestana,
                " situada en el borde derecho. Se desplegará la lista "
                "de laboratorios sin volver a Inicio.",
            ]

        progreso = [
            html.Span(
                className="sd-guia-progreso-punto"
                + (" sd-guia-progreso-punto-activo" if i <= indice else ""),
                key=str(i),
            )
            for i in range(len(pasos))
        ]

        return (
            "sd-guia sd-guia-visible" if abierto else "sd-guia sd-guia-oculta",
            "sd-guia-ayuda sd-guia-ayuda-oculta"
            if abierto or not pasos
            else "sd-guia-ayuda",
            f"Paso {indice + 1} de {len(pasos)}" if pasos else "",
            paso["titulo"],
            texto_paso,
            (
                [
                    html.Strong("PRUÉBALO", className="sd-guia-experimento-etiqueta"),
                    html.Span(paso.get("prueba", "")),
                ]
                if paso.get("prueba")
                else ""
            ),
            (
                "sd-guia-experimento"
                if paso.get("prueba")
                else "sd-guia-experimento sd-guia-experimento-oculto"
            ),
            progreso,
            indice == 0,
            "Finalizar ✓" if pasos and indice == len(pasos) - 1 else "Siguiente →",
            {
                "abierta": abierto,
                "pagina": pagina,
                "paso": indice,
                "objetivo": paso["objetivo"],
            },
        )

    # El JS se encarga solo del resaltado visual y su posicionamiento.
    app.clientside_callback(
        """function(escena) {
            if (window.SDTutorial && typeof window.SDTutorial.actualizar === 'function') {
                window.SDTutorial.actualizar(escena);
            }
            return JSON.stringify(escena || {});
        }""",
        Output("sd-guia-sincronizada", "data"),
        Input("sd-guia-escena", "data"),
    )
