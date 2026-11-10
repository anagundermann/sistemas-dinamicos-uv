"""Módulo de página: Simulador interactivo de Péndulo Doble N-Cuerpo (Diseño compacto 1 pantalla).

Diseñado para integrarse en la arquitectura multipágina de Sistemas Dinámicos UV.
Expone `crear_pagina()` y `registrar_callbacks(app)`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dash import Input, Output, State, dash_table, dcc, html

BG = "#FCFCFD"
PANEL = "#f5f5f7"
BORDER = "#2563C9"
TEXT = "#000000"
MUTED = "#000000"
ACCENT = "#B000F0"

CSS = f"""
.pd-app-container{{
    --bg-body:{BG};--bg-panel:{PANEL};--border:{BORDER};
    --text-main:{TEXT};--text-muted:{MUTED};--accent:{ACCENT};--btn-bg:#2a2a32;
    background:var(--bg-body);color:var(--text-main);
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    padding:14px 18px;border-radius:14px;width:100%;max-width:1500px;margin:auto;
    box-sizing:border-box;position:relative;
}}
.pd-app-container *{{box-sizing:border-box}}
.pd-app-container .header-bar{{
    display:flex;justify-content:space-between;align-items:center;
    gap:12px;flex-wrap:wrap;margin-bottom:10px;border-bottom:1px solid var(--border);
    padding-bottom:8px;
}}
.pd-app-container .header-right{{
    display:flex;align-items:center;gap:10px;flex-wrap:wrap;
}}
.pd-app-container h1{{font-size:19px;font-weight:700;margin:0;color:var(--text-main);letter-spacing:0.2px}}
.pd-app-container .subtitle{{color:#333333;font-size:13px;margin:4px 0 0}}
.pd-app-container .custom-tabs{{border-bottom:none!important;margin:0!important}}
.pd-app-container .custom-tab{{
    background:var(--bg-panel)!important;color:var(--text-muted)!important;
    border:1px solid var(--border)!important;padding:6px 14px!important;
    font-size:12px!important;margin-left:6px;border-radius:8px!important;
    text-align:center!important;display:flex!important;align-items:center!important;
    justify-content:center!important
}}
.pd-app-container .custom-tab--selected{{
    background:#25252d!important;color:var(--accent)!important;
    border:1px solid var(--accent)!important;font-weight:600!important;
}}

/* Botones disparadores de pestañas emergentes (Conceptos) */
.pd-app-container .concept-triggers{{
    display:flex;gap:6px;align-items:center;flex-wrap:wrap;
}}
.pd-app-container .concept-btn{{
    background:var(--bg-panel);border:1px solid var(--border);color:var(--text-main);
    padding:5px 12px;border-radius:20px;cursor:pointer;font-size:12px;
    font-weight:500;transition:.15s;display:inline-flex;align-items:center;gap:5px;
}}
.pd-app-container .concept-btn:hover{{
    border-color:var(--accent);color:var(--accent);background:var(--btn-bg);
}}

/* Ventana modal de pestañas emergentes con animación de emergencia y desvanecimiento */
.pd-app-container .pd-modal-overlay{{
    position:fixed;top:0;left:0;width:100vw;height:100vh;
    background:rgba(0,0,0,0.65);backdrop-filter:blur(3px);
    z-index:9999;display:flex;justify-content:center;align-items:center;
    padding:20px;
    opacity:0;visibility:hidden;pointer-events:none;
    transition:opacity 0.22s ease, visibility 0.22s ease;
}}
.pd-app-container .pd-modal-overlay.is-open{{
    opacity:1;visibility:visible;pointer-events:auto;
}}
.pd-app-container .pd-modal-card{{
    background:var(--bg-body);color:var(--text-main);
    border:1px solid var(--border);border-radius:16px;
    width:100%;max-width:920px;max-height:88vh;
    display:flex;flex-direction:column;
    box-shadow:0 20px 50px rgba(0,0,0,0.5);overflow:hidden;
    transform:translateY(22px) scale(0.95);opacity:0;
    transition:transform 0.24s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.2s ease;
}}
.pd-app-container .pd-modal-overlay.is-open .pd-modal-card{{
    transform:translateY(0) scale(1);opacity:1;
}}
.pd-app-container .pd-modal-header{{
    display:flex;justify-content:space-between;align-items:center;
    padding:14px 20px;background:var(--bg-panel);
    border-bottom:1px solid var(--border);gap:12px;flex-wrap:wrap;
}}
.pd-app-container .pd-modal-tabs{{
    display:flex;gap:8px;flex-wrap:wrap;
}}
.pd-app-container .pd-modal-tab{{
    background:transparent;border:1px solid var(--border);color:var(--text-muted);
    padding:6px 14px;border-radius:20px;cursor:pointer;font-size:12.5px;
    font-weight:500;transition:background 0.18s ease, color 0.18s ease, border-color 0.18s ease, transform 0.15s ease;
}}
.pd-app-container .pd-modal-tab.active{{
    background:var(--btn-bg);color:var(--accent);
    border-color:var(--accent);font-weight:600;
}}
.pd-app-container .pd-modal-close{{
    background:transparent;border:1px solid var(--border);color:var(--text-muted);
    width:32px;height:32px;border-radius:50%;cursor:pointer;font-size:15px;
    display:flex;align-items:center;justify-content:center;transition:.15s;
}}
.pd-app-container .pd-modal-close:hover{{
    border-color:var(--accent);color:var(--accent);
}}
.pd-app-container .pd-modal-body{{
    padding:20px 24px;overflow-y:auto;overflow-x:hidden;line-height:1.65;font-size:13.5px;
}}
.pd-app-container .pd-modal-body a{{
    color:#0066cc!important;text-decoration:underline;font-weight:600;cursor:pointer;
}}
.pd-app-container .pd-modal-body a:hover{{
    color:#004499!important;
}}

/* Animaciones horizontales al cambiar entre pestañas de conceptos */
@keyframes pdSlideFromRight{{
    0%{{opacity:0;transform:translateX(48px)}}
    100%{{opacity:1;transform:translateX(0)}}
}}
@keyframes pdSlideFromLeft{{
    0%{{opacity:0;transform:translateX(-48px)}}
    100%{{opacity:1;transform:translateX(0)}}
}}
@keyframes pdBodyEmerge{{
    0%{{opacity:0;transform:translateY(8px)}}
    100%{{opacity:1;transform:translateY(0)}}
}}
.pd-app-container .pd-modal-body.anim-right{{
    animation:pdSlideFromRight 0.25s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}}
.pd-app-container .pd-modal-body.anim-left{{
    animation:pdSlideFromLeft 0.25s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}}
.pd-app-container .pd-modal-body.anim-emerge{{
    animation:pdBodyEmerge 0.22s ease-out forwards;
}}

.pd-app-container .pd-modal-body h3{{
    margin:0 0 10px;color:var(--accent);font-size:17px;font-weight:600;
}}
.pd-app-container .pd-modal-body h4{{
    margin:12px 0 6px;color:var(--text-main);font-size:14px;font-weight:600;
}}
.pd-app-container .pd-modal-body p{{
    margin:0 0 10px;
}}
.pd-app-container .pd-modal-body ul{{
    margin:0 0 8px;padding-left:20px;
}}
.pd-app-container .pd-modal-body li{{
    margin-bottom:6px;
}}
.pd-app-container .pd-formula-box{{
    background:var(--bg-panel);border:1px solid var(--border);
    border-left:3px solid var(--accent);border-radius:8px;
    padding:10px 16px;margin:10px 0;font-size:14px;
    color:var(--text-main);overflow-x:auto;
    display:flex;flex-direction:column;gap:6px;
}}
.pd-app-container .pd-formula-box p{{
    margin:0!important;
}}
.pd-app-container .pd-concept-grid{{
    display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:10px;
}}
.pd-app-container .pd-concept-box{{
    background:var(--bg-panel);border:1px solid var(--border);
    border-radius:10px;padding:12px 14px;
}}
.pd-app-container .pd-concept-box h4{{
    margin-top:0;
}}

.pd-app-container .top-controls{{
    display:flex;justify-content:space-between;align-items:center;
    gap:10px;flex-wrap:wrap;margin-bottom:10px;
}}
.pd-app-container .indicators,.pd-app-container .action-row{{
    display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0;
}}
.pd-app-container .pill{{
    background:var(--bg-panel);border:1px solid var(--border);
    padding:4px 11px;border-radius:16px;font:12px monospace;color:var(--text-muted);
}}
.pd-app-container .pill span{{color:var(--text-main);font-weight:bold}}
.pd-app-container .action-btn{{
    background:var(--bg-panel);
    border:1px solid var(--border);
    color:var(--text-main);
    padding:7px 16px;
    border-radius:20px;
    cursor:pointer;
    font-size:12.5px;
    transition:.15s;
    font-weight:500;
}}
.pd-app-container .action-btn:hover{{
    background:var(--btn-bg);
    color:var(--accent);
    border-color:var(--accent);
}}
.pd-app-container .action-btn,
.pd-app-container .concept-btn,
.pd-app-container .switch-lab-btn{{
    box-shadow:0 1px 4px rgba(0,0,0,0.04);
}}
.pd-app-container .action-btn.primary{{border-color:#2563C9}}
.pd-app-container .action-btn.accent-active{{border-color:var(--accent);color:var(--accent)}}

/* Grilla principal en 3 columnas para caber sin scroll vertical */
.pd-app-container .workspace-grid{{
    display:grid;
    grid-template-columns:1.1fr 1fr 1.15fr;
    gap:12px;
    align-items:stretch;
}}
.pd-app-container .right-column{{display:flex;flex-direction:column;gap:12px}}
.pd-app-container .panel,.pd-app-container .info-card{{
    background:var(--bg-panel);
    border:1px solid var(--border);
    border-radius:12px;
    padding:10px 12px;
    min-width:0;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}}
.pd-app-container .panel-title{{
    font-size:11.5px;
    text-transform:uppercase;
    letter-spacing:0.9px;
    color:#333333;
    margin-bottom:8px;
    font-weight:600;
}}
.pd-app-container .canvas-host{{position:relative;width:100%}}
.pd-app-container .canvas-host canvas{{display:block;width:100%;height:100%}}
.pd-app-container .canvas-physics-size{{height:350px;min-height:280px}}
.pd-app-container .canvas-chart-size{{height:156px;min-height:130px}}

/* Panel de Sliders compacto a la derecha */
.pd-app-container .sliders-panel{{
    background:var(--bg-panel);border:1px solid var(--border);
    border-radius:10px;padding:10px 14px;
    display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
    gap:7px 16px;align-content:space-between;
}}
.pd-app-container .slider-group{{min-width:0}}
.pd-app-container .slider-group.full-span{{grid-column:1 / -1}}
.pd-app-container .slider-header{{
    display:flex;justify-content:space-between;align-items:center;
    gap:6px;font-size:11.5px;color:var(--text-muted);margin-bottom:3px;
}}
.pd-app-container .slider-header .val{{color:var(--text-main);font-family:monospace;white-space:nowrap}}
.pd-app-container .rc-slider{{padding:4px 0!important}}
.pd-app-container .rc-slider-rail{{background-color:var(--border)!important;height:4px!important}}
.pd-app-container .rc-slider-track{{background-color:var(--text-main)!important;height:4px!important}}
.pd-app-container .rc-slider-handle{{
    background-color:var(--text-main)!important;border:0!important;
    width:11px!important;height:11px!important;margin-top:-3.5px!important;box-shadow:none!important;
}}
.pd-app-container .speed-buttons{{display:flex;align-items:center;gap:4px;flex-wrap:wrap}}
.pd-app-container .btn-small{{
    background:transparent;border:1px solid var(--accent);color:var(--accent);
    border-radius:4px;cursor:pointer;font:10px monospace;padding:1px 5px;
}}
.pd-app-container .info-card{{line-height:1.5;font-size:13px;margin-bottom:12px;color:var(--text-main)}}
.pd-app-container .info-card h3{{margin:0 0 6px;color:var(--text-main);font-size:16px;font-weight:700}}
.pd-app-container .note{{color:var(--text-muted);font-size:11px;line-height:1.4}}

/* Botón inferior de transición rápida entre Péndulo Simple y Péndulo Doble */
.pd-app-container .switch-lab-row{{
    display:flex;justify-content:flex-start;align-items:center;margin-top:10px;
}}
.pd-app-container .switch-lab-btn{{
    background:var(--bg-panel);border:1px solid var(--border);color:var(--text-main);
    padding:6px 16px;border-radius:20px 6px 6px 20px;cursor:pointer;
    font:12.5px monospace;font-weight:600;display:inline-flex;align-items:center;
    gap:8px;transition:.15s;
}}
.pd-app-container .switch-lab-btn:hover{{
    border-color:var(--accent);color:var(--accent);background:var(--btn-bg);
}}

@media(max-width:1100px){{
    .pd-app-container .workspace-grid{{grid-template-columns:1fr 1fr}}
    .pd-app-container .sliders-panel{{grid-column:1 / -1;grid-template-columns:repeat(3,minmax(0,1fr))}}
}}
@media(max-width:720px){{
    .pd-app-container .workspace-grid{{grid-template-columns:1fr}}
    .pd-app-container .sliders-panel{{grid-template-columns:1fr}}
    .pd-app-container .pd-concept-grid{{grid-template-columns:1fr}}
}}
"""

initial_table_columns = [
    {"name": "Tiempo t (s)", "id": "tiempo"},
    {"name": "log₁₀(Δθ)", "id": "divergencia"},
    {"name": "Ángulo θ₁ (rad)", "id": "fase_x"},
    {"name": "Ángulo θ₂ (rad)", "id": "fase_y"},
    {"name": "Energía cinética (J)", "id": "energia_cinetica"},
    {"name": "Energía potencial (J)", "id": "energia_potencial"},
    {"name": "Energía total (J)", "id": "energia_total"},
]


def slider(
    label, sid, minimum, maximum, step, value, value_id, display, full_span=False
):
    cls = "slider-group full-span" if full_span else "slider-group"
    return html.Div(
        className=cls,
        children=[
            html.Div(
                className="slider-header",
                children=[
                    html.Span(label),
                    html.Span(display, id=value_id, className="val"),
                ],
            ),
            dcc.Slider(
                id=sid,
                min=minimum,
                max=maximum,
                step=step,
                value=value,
                marks=None,
                updatemode="drag",
                persistence=True,
                persistence_type="memory",
            ),
        ],
    )


def crear_modal_conceptos_doble():
    """Construye la ventana emergente con las 3 pestañas de conceptos del Péndulo Doble en LaTeX."""
    return html.Div(
        id="pd-modal-overlay",
        className="pd-modal-overlay",
        children=[
            html.Div(
                className="pd-modal-card",
                children=[
                    html.Div(
                        className="pd-modal-header",
                        children=[
                            html.Div(
                                className="pd-modal-tabs",
                                children=[
                                    html.Button(
                                        "¿Qué es el péndulo doble?",
                                        id="pd-tab-modal-fisico",
                                        n_clicks=0,
                                        className="pd-modal-tab active",
                                    ),
                                    html.Button(
                                        "Modelo matemático",
                                        id="pd-tab-modal-modelo",
                                        n_clicks=0,
                                        className="pd-modal-tab",
                                    ),
                                    html.Button(
                                        "Análisis del sistema y caos",
                                        id="pd-tab-modal-analisis",
                                        n_clicks=0,
                                        className="pd-modal-tab",
                                    ),
                                ],
                            ),
                            html.Button(
                                "✕",
                                id="pd-btn-modal-cerrar",
                                n_clicks=0,
                                className="pd-modal-close",
                                title="Cerrar",
                            ),
                        ],
                    ),
                    # Contenido 1: ¿Qué es el péndulo doble?
                    html.Div(
                        id="pd-modal-body-fisico",
                        className="pd-modal-body",
                        style={"display": "block"},
                        children=[
                            dcc.Markdown(
                                r"""
### ¿Qué es el Péndulo Doble?
El **péndulo doble** es un sistema mecánico no lineal con **dos grados de libertad** cuya [variedad de configuración](https://es.wikipedia.org/wiki/Espacio_de_configuraci%C3%B3n) es el 2-toro $\mathbb{T}^2 = S^1 \times S^1$, parametrizado por los ángulos $(\theta_1, \theta_2)$ medidos respecto a la vertical. Consta de una primera masa puntual $m_1$ unida a un pivote fijo por un brazo rígido de longitud $L_1$, y una segunda masa $m_2$ articulada libremente al extremo de $m_1$ mediante un brazo de longitud $L_2$.

Las posiciones cartesianas instantáneas de ambas partículas con respecto al pivote central vienen dadas por:
                                """,
                                mathjax=True,
                                link_target="_blank",
                            ),
                            html.Div(
                                className="pd-formula-box",
                                children=[
                                    dcc.Markdown(
                                        r"$$x_1(t) = L_1\sin\theta_1(t), \qquad y_1(t) = -L_1\cos\theta_1(t)$$",
                                        mathjax=True,
                                    ),
                                    dcc.Markdown(
                                        r"$$x_2(t) = L_1\sin\theta_1(t) + L_2\sin\theta_2(t), \qquad y_2(t) = -L_1\cos\theta_1(t) - L_2\cos\theta_2(t)$$",
                                        mathjax=True,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="pd-concept-grid",
                                children=[
                                    html.Div(
                                        className="pd-concept-box",
                                        children=dcc.Markdown(
                                            r"""
#### Supuestos y acoplamiento dinámico
* **Masas puntuales regulables:** Las esferas $m_1$ y $m_2$ ($0.2\text{ a }5.0\text{ kg}$) modifican el cociente de inercia $m_2/m_1$: si $m_1 \gg m_2$ el primer brazo actúa casi como un péndulo simple forzando al segundo; si $m_2 \gg m_1$ la retroacción centrífuga sobre el primer eslabón se intensifica.
* **Acoplamiento inercial no lineal:** La matriz de inercia depende del desfase angular $\Delta = \theta_1 - \theta_2$, generando torques centrífugos ($\propto \omega_i^2\sin\Delta$) y de reacción entre ambos brazos.
* **Ensamble de $N$ trayectorias:** Se integran simultáneamente $N$ péndulos dobles separados inicialmente por una perturbación infinitesimal $\Delta\theta_0 = 10^{\log_{10}(\Delta\theta_0)}$.
                                            """,
                                            mathjax=True,
                                            link_target="_blank",
                                        ),
                                    ),
                                    html.Div(
                                        className="pd-concept-box",
                                        children=dcc.Markdown(
                                            r"""
#### Regímenes dinámicos para explorar
* **Baja energía ($|\theta_1|, |\theta_2| < 20^\circ$):** Oscilaciones cuasiperiódicas regulares gobernadas por la superposición lineal de dos modos normales (en fase $\omega_-$ y en contrafase $\omega_+$).
* **Alta energía (ej. $\theta_1 = 180^\circ, \theta_2 = -10^\circ$):** Transición al **caos determinista**, con volteretas completas del segundo eslabón y separación exponencial del haz de péndulos.
* **Ingravidez ($g = 0\text{ m/s}^2$):** Aparece invarianza rotacional global, conservándose el momento angular total y desapareciendo el comportamiento caótico.
                                            """,
                                            mathjax=True,
                                            link_target="_blank",
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Contenido 2: Modelo matemático
                    html.Div(
                        id="pd-modal-body-modelo",
                        className="pd-modal-body",
                        style={"display": "none"},
                        children=[
                            dcc.Markdown(
                                r"""
### Modelo Matemático (Ecuaciones de Euler-Lagrange en $\mathbb{T}^2$)
A partir de las velocidades cartesianas $(\dot{x}_i, \dot{y}_i)$, la energía cinética total $T(\theta_1, \theta_2, \dot{\theta}_1, \dot{\theta}_2)$ y la energía potencial gravitatoria $V(\theta_1, \theta_2)$ definen el [Lagrangiano](https://es.wikipedia.org/wiki/Lagrangiano) $\mathcal{L} = T - V$:
                                """,
                                mathjax=True,
                                link_target="_blank",
                            ),
                            html.Div(
                                className="pd-formula-box",
                                children=[
                                    dcc.Markdown(
                                        r"$$T = \frac{1}{2}(m_1 + m_2)L_1^2\dot{\theta}_1^2 + \frac{1}{2}m_2 L_2^2\dot{\theta}_2^2 + m_2 L_1 L_2 \dot{\theta}_1\dot{\theta}_2\cos(\theta_1 - \theta_2)$$",
                                        mathjax=True,
                                    ),
                                    dcc.Markdown(
                                        r"$$V = (m_1 + m_2)g L_1(1 - \cos\theta_1) + m_2 g L_2(1 - \cos\theta_2)$$",
                                        mathjax=True,
                                    ),
                                ],
                            ),
                            dcc.Markdown(
                                r"""
El estado evoluciona en la variedad de fases de **dimensión 4** $T^*\mathbb{T}^2 \cong \mathbb{T}^2 \times \mathbb{R}^2$ con vector $x = (\theta_1, \omega_1, \theta_2, \omega_2)^\top$. Definiendo la diferencia angular $\Delta = \theta_1 - \theta_2$ y el denominador efectivo de inercia $D(\Delta) = 2m_1 + m_2 - m_2\cos(2\Delta) > 0$, el sistema de EDOs acopladas integrado mediante **RK4** es:
                                """,
                                mathjax=True,
                                link_target="_blank",
                            ),
                            html.Div(
                                className="pd-formula-box",
                                children=[
                                    dcc.Markdown(
                                        r"$$\dot{\theta}_1 = \omega_1, \qquad \dot{\theta}_2 = \omega_2$$",
                                        mathjax=True,
                                    ),
                                    dcc.Markdown(
                                        r"$$\dot{\omega}_1 = \frac{-g(2m_1+m_2)\sin\theta_1 - m_2 g\sin(\theta_1 - 2\theta_2) - 2m_2\sin\Delta\left(\omega_2^2 L_2 + \omega_1^2 L_1\cos\Delta\right)}{L_1 D(\Delta)} - b\omega_1$$",
                                        mathjax=True,
                                    ),
                                    dcc.Markdown(
                                        r"$$\dot{\omega}_2 = \frac{2\sin\Delta\left(\omega_1^2 L_1(m_1+m_2) + g(m_1+m_2)\cos\theta_1 + \omega_2^2 L_2 m_2\cos\Delta\right)}{L_2 D(\Delta)} - b\omega_2$$",
                                        mathjax=True,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Contenido 3: Análisis del sistema y caos
                    html.Div(
                        id="pd-modal-body-analisis",
                        className="pd-modal-body",
                        style={"display": "none"},
                        children=[
                            dcc.Markdown(
                                r"""
### Análisis del Sistema, No-Integrabilidad y Caos Determinista
Por el [Teorema de Liouville-Arnold](https://en.wikipedia.org/wiki/Liouville%E2%80%93Arnold_theorem), un sistema [hamiltoniano](https://es.wikipedia.org/wiki/Hamiltoniano_%28mec%C3%A1nica_cl%C3%A1sica%29) de $n = 2$ grados de libertad (espacio de fases de dimensión $2n = 4$) requiere dos integrales primeras independientes en involución para ser integrable por cuadraturas. Cuando $g > 0$ y $b = 0$, la única cantidad conservada es la energía total $E = T + V$, rompiéndose la integrabilidad global.
                                """,
                                mathjax=True,
                                link_target="_blank",
                            ),
                            html.Div(
                                className="pd-concept-grid",
                                children=[
                                    html.Div(
                                        className="pd-concept-box",
                                        children=dcc.Markdown(
                                            r"""
#### Los 4 Puntos de Equilibrio ($\nabla V = 0$)
* **$(0, 0)$ Abajo-Abajo ($E=0$):** Mínimo global con matriz Hessiana definida positiva $D^2V(0,0) \succ 0$ (**centro estable**).
* **$(0, \pi)$ Abajo-Arriba:** Punto de silla inestable de índice de Morse $1$ ($E = 2m_2 g L_2$).
* **$(\pi, 0)$ Arriba-Abajo:** Punto de silla inestable de índice $1$ ($E = 2(m_1+m_2)g L_1$).
* **$(\pi, \pi)$ Arriba-Arriba:** Máximo global de potencial, silla inestable de índice $2$ ($E = 2(m_1+m_2)g L_1 + 2m_2 g L_2$).
                                            """,
                                            mathjax=True,
                                            link_target="_blank",
                                        ),
                                    ),
                                    html.Div(
                                        className="pd-concept-box",
                                        children=dcc.Markdown(
                                            r"""
#### Teoría KAM y Exponente de Lyapunov ($\lambda_{\max}$) [?(1)](https://en.wikipedia.org/wiki/Lyapunov_exponent) , [?(2)](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Arnold%E2%80%93Moser_theorem)
* **Ruptura de toros KAM:** A baja energía predominan toros invariantes $\mathbb{T}^2$ cuasiperiódicos; al crecer $E$, las resonancias no lineales destruyen dichos toros generando caos.
* **Divergencia exponencial:** Dos trayectorias separadas por $\Delta\theta_0$ divergen con tasa media dada por el exponente máximo de Lyapunov $\lambda_{\max} > 0$:
                                            """,
                                            mathjax=True,
                                            link_target="_blank",
                                        ),
                                    ),
                                ],
                            ),
                            html.Div(
                                className="pd-formula-box",
                                children=[
                                    dcc.Markdown(
                                        r"$$\Delta\theta(t) \approx \Delta\theta_0 e^{\lambda_{\max} t} \quad \Longleftrightarrow \quad \log_{10}(\Delta\theta(t)) \approx \log_{10}(\Delta\theta_0) + \left(\frac{\lambda_{\max}}{\ln 10}\right)t, \qquad t_{\text{horizonte}} \approx \frac{1}{\lambda_{\max}}\ln\left(\frac{\pi}{\Delta\theta_0}\right)$$",
                                        mathjax=True,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


def crear_pagina():
    return html.Div(
        className="pd-app-container",
        style={"--border": BORDER},
        children=[
            dcc.Store(id="pd-client-sync", data=0),
            dcc.Store(id="pd-analysis-store", data=None),
            dcc.Download(id="pd-download-csv"),
            # Ventana emergente de conceptos (oculta por defecto con opacidad 0)
            crear_modal_conceptos_doble(),
            # Cabecera + Botones emergentes de conceptos + Pestañas en una sola línea
            html.Div(
                className="header-bar",
                children=[
                    html.Div(
                        [
                            html.H1("Simulador Interactivo de Péndulo Doble N-Cuerpo"),
                            html.Div(
                                "Dinámica no lineal, sensibilidad a condiciones iniciales y caos determinista mediante RK4",
                                className="subtitle",
                            ),
                        ]
                    ),
                    html.Div(
                        className="header-right",
                        children=[
                            html.Div(
                                className="concept-triggers",
                                children=[
                                    html.Button(
                                        "¿Qué es el péndulo doble?",
                                        id="pd-btn-modal-fisico",
                                        n_clicks=0,
                                        className="concept-btn",
                                    ),
                                    html.Button(
                                        "Modelo matemático",
                                        id="pd-btn-modal-modelo",
                                        n_clicks=0,
                                        className="concept-btn",
                                    ),
                                    html.Button(
                                        "Análisis del sistema y caos",
                                        id="pd-btn-modal-analisis",
                                        n_clicks=0,
                                        className="concept-btn",
                                    ),
                                ],
                            ),
                            dcc.Tabs(
                                id="pd-tabs-navigation",
                                value="tab-simulador",
                                className="custom-tabs",
                                persistence=True,
                                persistence_type="memory",
                                children=[
                                    dcc.Tab(
                                        label="1. Simulador",
                                        value="tab-simulador",
                                        className="custom-tab",
                                        selected_className="custom-tab--selected",
                                    ),
                                    dcc.Tab(
                                        label="2. Mediciones y guía teórica",
                                        value="tab-datos",
                                        className="custom-tab",
                                        selected_className="custom-tab--selected",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # CONTENEDOR PERSISTENTE 1: SIMULADOR COMPACTO EN 1 PANTALLA
            html.Div(
                id="pd-panel-simulador",
                style={"display": "block"},
                children=[
                    html.Div(
                        className="top-controls",
                        children=[
                            html.Div(
                                className="indicators",
                                children=[
                                    html.Div(
                                        className="pill",
                                        children=[
                                            "Tiempo t: ",
                                            html.Span("0.000 s", id="pd-ind-time"),
                                        ],
                                    ),
                                    html.Div(
                                        className="pill",
                                        children=[
                                            "Δθ máx: ",
                                            html.Span("0.00e+0 rad", id="pd-ind-div"),
                                        ],
                                    ),
                                    html.Div(
                                        className="pill",
                                        children=[
                                            "Energía E: ",
                                            html.Span("0.00 J", id="pd-ind-energy"),
                                        ],
                                    ),
                                    html.Div(
                                        className="pill",
                                        children=[
                                            "FPS: ",
                                            html.Span("—", id="pd-ind-fps"),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="action-row",
                                children=[
                                    html.Button(
                                        "Iniciar",
                                        id="pd-btn-iniciar",
                                        n_clicks=0,
                                        className="action-btn primary",
                                    ),
                                    html.Button(
                                        "Reiniciar a t=0",
                                        id="pd-btn-reiniciar",
                                        n_clicks=0,
                                        className="action-btn",
                                    ),
                                    html.Button(
                                        "Limpiar Estelas",
                                        id="pd-btn-limpiar",
                                        n_clicks=0,
                                        className="action-btn",
                                    ),
                                    html.Button(
                                        "Fijar Estelas",
                                        id="pd-btn-fijar",
                                        n_clicks=0,
                                        className="action-btn",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="workspace-grid",
                        children=[
                            html.Div(
                                className="panel",
                                children=[
                                    html.Div(
                                        "VISTA FÍSICA (PÉNDULO DOBLE)",
                                        id="pd-title-fisica",
                                        className="panel-title",
                                    ),
                                    html.Div(
                                        id="pd-canvas-physics-host",
                                        className="canvas-host canvas-physics-size",
                                    ),
                                ],
                            ),
                            html.Div(
                                className="right-column",
                                children=[
                                    html.Div(
                                        className="panel",
                                        children=[
                                            html.Div(
                                                "DIVERGENCIA DE TRAYECTORIAS log₁₀(Δθ)",
                                                className="panel-title",
                                            ),
                                            html.Div(
                                                id="pd-canvas-div-host",
                                                className="canvas-host canvas-chart-size",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="panel",
                                        children=[
                                            html.Div(
                                                "ESPACIO DE CONFIGURACIÓN (θ₁ vs θ₂)",
                                                id="pd-title-fase",
                                                className="panel-title",
                                            ),
                                            html.Div(
                                                id="pd-canvas-phase-host",
                                                className="canvas-host canvas-chart-size",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="sliders-panel",
                                children=[
                                    slider(
                                        "θ₁ Inicial (°)",
                                        "pd-sl-t1",
                                        -180,
                                        180,
                                        1,
                                        180,
                                        "pd-val-t1",
                                        "180°",
                                    ),
                                    slider(
                                        "θ₂ Inicial (°)",
                                        "pd-sl-t2",
                                        -180,
                                        180,
                                        1,
                                        -10,
                                        "pd-val-t2",
                                        "-10°",
                                    ),
                                    slider(
                                        "N.º péndulos (N)",
                                        "pd-sl-n",
                                        1,
                                        12,
                                        1,
                                        5,
                                        "pd-val-n",
                                        "5",
                                    ),
                                    slider(
                                        "Perturbación log₁₀(Δθ₀)",
                                        "pd-sl-dt",
                                        -6,
                                        0,
                                        0.1,
                                        -3,
                                        "pd-val-dt",
                                        "-3.0",
                                    ),
                                    slider(
                                        "Longitud L₁ (m)",
                                        "pd-sl-l1",
                                        0.5,
                                        3,
                                        0.1,
                                        2,
                                        "pd-val-l1",
                                        "2.0 m",
                                    ),
                                    slider(
                                        "Longitud L₂ (m)",
                                        "pd-sl-l2",
                                        0.5,
                                        3,
                                        0.1,
                                        1,
                                        "pd-val-l2",
                                        "1.0 m",
                                    ),
                                    slider(
                                        "Gravedad g (m/s²)",
                                        "pd-sl-g",
                                        0,
                                        25,
                                        0.1,
                                        9.8,
                                        "pd-val-g",
                                        "9.8 m/s²",
                                    ),
                                    slider(
                                        "Amortiguamiento b (s⁻¹)",
                                        "pd-sl-b",
                                        0,
                                        0.5,
                                        0.01,
                                        0,
                                        "pd-val-b",
                                        "0.00",
                                    ),
                                    slider(
                                        "Masa 1 m₁ (kg)",
                                        "pd-sl-m1",
                                        0.1,
                                        10.0,
                                        0.1,
                                        1.0,
                                        "pd-val-m1",
                                        "1.0 kg",
                                    ),
                                    slider(
                                        "Masa 2 m₂ (kg)",
                                        "pd-sl-m2",
                                        0.1,
                                        10.0,
                                        0.1,
                                        1.0,
                                        "pd-val-m2",
                                        "1.0 kg",
                                    ),
                                    html.Div(
                                        className="slider-group full-span",
                                        children=[
                                            html.Div(
                                                className="slider-header",
                                                children=[
                                                    html.Span(
                                                        "Velocidad de simulación"
                                                    ),
                                                    html.Div(
                                                        className="speed-buttons",
                                                        children=[
                                                            html.Span(
                                                                "1.0x",
                                                                id="pd-val-speed",
                                                                className="val",
                                                            ),
                                                            html.Button(
                                                                "x0.5",
                                                                id="pd-btn-half",
                                                                n_clicks=0,
                                                                className="btn-small",
                                                            ),
                                                            html.Button(
                                                                "x2",
                                                                id="pd-btn-x2",
                                                                n_clicks=0,
                                                                className="btn-small",
                                                            ),
                                                            html.Button(
                                                                "↺",
                                                                id="pd-btn-reset-speed",
                                                                n_clicks=0,
                                                                className="btn-small",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            dcc.Slider(
                                                id="pd-sl-speed",
                                                min=0.1,
                                                max=10,
                                                step=0.1,
                                                value=1,
                                                marks=None,
                                                updatemode="drag",
                                                persistence=True,
                                                persistence_type="memory",
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Botón inferior izquierdo para ir inmediatamente a Péndulo Simple
                    html.Div(
                        className="switch-lab-row",
                        children=[
                            html.Button(
                                "◀ Péndulo simple",
                                id="pd-btn-ir-simple",
                                n_clicks=0,
                                className="switch-lab-btn",
                                title="Ir al simulador de Péndulo Simple",
                            ),
                        ],
                    ),
                ],
            ),
            # CONTENEDOR PERSISTENTE 2: MEDICIONES Y GUÍA TEÓRICA
            html.Div(
                id="pd-panel-datos",
                style={"display": "none"},
                children=[
                    html.Div(
                        className="info-card",
                        children=[
                            html.H3("Motivación, supuestos y uso (Péndulo Doble)"),
                            dcc.Markdown(
                                r"""
Este simulador permite explorar la sensibilidad extrema a las condiciones iniciales (*efecto mariposa*) y el caos determinista en un sistema de $N$ péndulos dobles acoplados.

**Supuestos:** masas puntuales $m_1$ y $m_2$ ajustables entre $0.2\text{ y }5.0\text{ kg}$, barras rígidas sin masa de longitudes $L_1$ y $L_2$, gravedad uniforme $g$ y amortiguamiento $b$ proporcional a cada velocidad angular. Las ecuaciones de Euler-Lagrange se integran mediante Runge-Kutta de 4.º orden (RK4). A alta energía y con $g > 0$, la inexistencia de una segunda integral de movimiento (Teorema de Liouville-Arnold) produce divergencia exponencial $\Delta\theta(t) \sim \Delta\theta_0 e^{\lambda_{\max} t}$ entre trayectorias inicialmente separadas por $\Delta\theta_0$.
                                """,
                                mathjax=True,
                            ),
                            html.Div(
                                style={
                                    "marginTop": "12px",
                                    "display": "flex",
                                    "gap": "10px",
                                    "alignItems": "center",
                                    "flexWrap": "wrap",
                                },
                                children=[
                                    html.Button(
                                        "Actualizar tabla con estado actual",
                                        id="pd-btn-capturar",
                                        n_clicks=0,
                                        className="action-btn primary",
                                    ),
                                    html.Button(
                                        "⬇ Descargar CSV",
                                        id="pd-btn-download-csv",
                                        n_clicks=0,
                                        className="action-btn",
                                    ),
                                    html.Span(
                                        id="pd-analysis-status",
                                        className="note",
                                        style={"marginLeft": "10px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="panel",
                        children=[
                            html.Div(
                                "REGISTRO HISTÓRICO DE LA CAPTURA (PÉNDULO DOBLE)",
                                className="panel-title",
                            ),
                            dash_table.DataTable(
                                id="pd-tabla-mediciones",
                                columns=initial_table_columns,
                                data=[],
                                page_size=10,
                                style_table={"overflowX": "auto"},
                                style_header={
                                    "backgroundColor": "#a2a2a7",
                                    "color": TEXT,
                                    "fontWeight": "bold",
                                    "border": f"1px solid {BORDER}",
                                },
                                style_cell={
                                    "backgroundColor": PANEL,
                                    "color": TEXT,
                                    "border": f"1px solid {BORDER}",
                                    "fontFamily": "monospace",
                                    "textAlign": "center",
                                    "padding": "6px",
                                    "minWidth": "100px",
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"row_index": "odd"},
                                        "backgroundColor": "#a2a2a7",
                                    }
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def registrar_callbacks(app):
    if "</head>" in app.index_string and "pd-scoped-styles" not in app.index_string:
        app.index_string = app.index_string.replace(
            "</head>", f'<style id="pd-scoped-styles">{CSS}</style></head>'
        )

    # Transición inmediata hacia Péndulo Simple
    app.clientside_callback(
        """function(nClicks) {
            if (!nClicks) return window.dash_clientside.no_update;
            const navBtn = document.getElementById('sd-nav-pendulo_simple');
            if (navBtn) navBtn.click();
            return window.dash_clientside.no_update;
        }""",
        Output("pd-btn-ir-simple", "n_clicks"),
        Input("pd-btn-ir-simple", "n_clicks"),
        prevent_initial_call=True,
    )

    # Control animado de las pestañas emergentes
    app.clientside_callback(
        """function(bFis, bMod, bAna, tFis, tMod, tAna, bClose) {
            const trig = window.dash_clientside.callback_context.triggered_id;
            const prevIdx = (typeof window._pdModalTabIdx === 'number') ? window._pdModalTabIdx : 0;
            const wasOpen = Boolean(window._pdModalOpen);

            if (!trig || trig === 'pd-btn-modal-cerrar') {
                window._pdModalOpen = false;
                return [
                    'pd-modal-overlay',
                    window.dash_clientside.no_update,
                    window.dash_clientside.no_update,
                    window.dash_clientside.no_update,
                    window.dash_clientside.no_update,
                    window.dash_clientside.no_update,
                    window.dash_clientside.no_update,
                    window.dash_clientside.no_update,
                    window.dash_clientside.no_update,
                    window.dash_clientside.no_update
                ];
            }

            let targetIdx = 0;
            if (trig === 'pd-btn-modal-fisico' || trig === 'pd-tab-modal-fisico') targetIdx = 0;
            else if (trig === 'pd-btn-modal-modelo' || trig === 'pd-tab-modal-modelo') targetIdx = 1;
            else if (trig === 'pd-btn-modal-analisis' || trig === 'pd-tab-modal-analisis') targetIdx = 2;

            let animClass = 'pd-modal-body anim-emerge';
            if (wasOpen && targetIdx !== prevIdx) {
                animClass = (targetIdx > prevIdx) ? 'pd-modal-body anim-right' : 'pd-modal-body anim-left';
            }

            window._pdModalOpen = true;
            window._pdModalTabIdx = targetIdx;

            setTimeout(function() {
                if (window.MathJax && window.MathJax.typesetPromise) {
                    window.MathJax.typesetPromise();
                }
            }, 30);

            return [
                'pd-modal-overlay is-open',
                {display: targetIdx === 0 ? 'block' : 'none'},
                {display: targetIdx === 1 ? 'block' : 'none'},
                {display: targetIdx === 2 ? 'block' : 'none'},
                targetIdx === 0 ? animClass : 'pd-modal-body',
                targetIdx === 1 ? animClass : 'pd-modal-body',
                targetIdx === 2 ? animClass : 'pd-modal-body',
                targetIdx === 0 ? 'pd-modal-tab active' : 'pd-modal-tab',
                targetIdx === 1 ? 'pd-modal-tab active' : 'pd-modal-tab',
                targetIdx === 2 ? 'pd-modal-tab active' : 'pd-modal-tab'
            ];
        }""",
        Output("pd-modal-overlay", "className"),
        Output("pd-modal-body-fisico", "style"),
        Output("pd-modal-body-modelo", "style"),
        Output("pd-modal-body-analisis", "style"),
        Output("pd-modal-body-fisico", "className"),
        Output("pd-modal-body-modelo", "className"),
        Output("pd-modal-body-analisis", "className"),
        Output("pd-tab-modal-fisico", "className"),
        Output("pd-tab-modal-modelo", "className"),
        Output("pd-tab-modal-analisis", "className"),
        Input("pd-btn-modal-fisico", "n_clicks"),
        Input("pd-btn-modal-modelo", "n_clicks"),
        Input("pd-btn-modal-analisis", "n_clicks"),
        Input("pd-tab-modal-fisico", "n_clicks"),
        Input("pd-tab-modal-modelo", "n_clicks"),
        Input("pd-tab-modal-analisis", "n_clicks"),
        Input("pd-btn-modal-cerrar", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """function(tabValue) {
            if (tabValue === 'tab-datos') {
                return [{display: 'none'}, {display: 'block'}];
            }
            setTimeout(function() {
                if (window.PendulumDoubleApp && typeof window.PendulumDoubleApp.refreshView === 'function') {
                    window.PendulumDoubleApp.refreshView();
                }
            }, 30);
            return [{display: 'block'}, {display: 'none'}];
        }""",
        Output("pd-panel-simulador", "style"),
        Output("pd-panel-datos", "style"),
        Input("pd-tabs-navigation", "value"),
    )

    app.clientside_callback(
        """function(t1,t2,n,logdt,l1,l2,g,b,m1,m2,speed,cStart,cReset,cClear,cFix) {
            if (!window.PendulumDoubleApp) return window.dash_clientside.no_update;
            window.PendulumDoubleApp.sync({t1,t2,n,logdt,l1,l2,g,b,m1,m2,speed,cStart,cReset,cClear,cFix});
            return (window.PendulumDoubleApp.syncCount || 0);
        }""",
        Output("pd-client-sync", "data"),
        Input("pd-sl-t1", "value"),
        Input("pd-sl-t2", "value"),
        Input("pd-sl-n", "value"),
        Input("pd-sl-dt", "value"),
        Input("pd-sl-l1", "value"),
        Input("pd-sl-l2", "value"),
        Input("pd-sl-g", "value"),
        Input("pd-sl-b", "value"),
        Input("pd-sl-m1", "value"),
        Input("pd-sl-m2", "value"),
        Input("pd-sl-speed", "value"),
        Input("pd-btn-iniciar", "n_clicks"),
        Input("pd-btn-reiniciar", "n_clicks"),
        Input("pd-btn-limpiar", "n_clicks"),
        Input("pd-btn-fijar", "n_clicks"),
    )

    app.clientside_callback(
        """function(nHalf,nDouble,nReset,current,maxValue) {
            const triggered = window.dash_clientside.callback_context.triggered_id;
            if (!triggered) return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            let value = Number(current), max = Number(maxValue);
            if (triggered === 'pd-btn-half') value = Math.max(0.1, value * 0.5);
            else if (triggered === 'pd-btn-x2') { value = value * 2; max = Math.max(max, value); }
            else if (triggered === 'pd-btn-reset-speed') { value = 1; max = 10; }
            else return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            value = Math.round(value * 10) / 10;
            return [value, max];
        }""",
        Output("pd-sl-speed", "value"),
        Output("pd-sl-speed", "max"),
        Input("pd-btn-half", "n_clicks"),
        Input("pd-btn-x2", "n_clicks"),
        Input("pd-btn-reset-speed", "n_clicks"),
        State("pd-sl-speed", "value"),
        State("pd-sl-speed", "max"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """function(nClicks, tabValue) {
            if (!window.PendulumDoubleApp) return window.dash_clientside.no_update;
            const triggered = window.dash_clientside.callback_context.triggered_id;
            if (triggered === 'pd-tabs-navigation' && tabValue !== 'tab-datos') {
                return window.dash_clientside.no_update;
            }
            return window.PendulumDoubleApp.snapshot();
        }""",
        Output("pd-analysis-store", "data"),
        Input("pd-btn-capturar", "n_clicks"),
        Input("pd-tabs-navigation", "value"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output("pd-tabla-mediciones", "data"),
        Output("pd-analysis-status", "children"),
        Input("pd-analysis-store", "data"),
    )
    def update_table_double(data):
        if not data or not data.get("time"):
            return [], "Todavía no hay datos capturados."

        t = np.asarray(data.get("time", []), dtype=float)
        div = np.asarray(data.get("div", []), dtype=float)
        et = np.asarray(data.get("energy_t", []), dtype=float)
        ev = np.asarray(data.get("energy_v", []), dtype=float)
        ee = np.asarray(data.get("energy_total", []), dtype=float)
        px = np.asarray(data.get("phase_x", []), dtype=float)
        py = np.asarray(data.get("phase_y", []), dtype=float)

        n = min(len(t), len(div), len(et), len(ev), len(ee), len(px), len(py))
        t, div, et, ev, ee, px, py = [a[:n] for a in (t, div, et, ev, ee, px, py)]

        if n == 0:
            return [], "La captura no contiene muestras."

        rows = [
            {
                "tiempo": round(float(ti), 6),
                "divergencia": round(float(di), 8),
                "fase_x": round(float(xi), 8),
                "fase_y": round(float(yi), 8),
                "energia_cinetica": round(float(kti), 8),
                "energia_potencial": round(float(kvi), 8),
                "energia_total": round(float(kei), 8),
            }
            for ti, di, xi, yi, kti, kvi, kei in zip(t, div, px, py, et, ev, ee)
        ][::-1]

        status = (
            f"Captura actualizada: {n} muestras registradas (hasta t = {t[-1]:.3f} s)."
        )
        return rows, status

    @app.callback(
        Output("pd-download-csv", "data"),
        Input("pd-btn-download-csv", "n_clicks"),
        State("pd-analysis-store", "data"),
        prevent_initial_call=True,
    )
    def download_csv_double(_clicks, data):
        if not data or not data.get("time"):
            return None
        n = min(
            len(data.get(k, []))
            for k in (
                "time",
                "div",
                "phase_x",
                "phase_y",
                "energy_t",
                "energy_v",
                "energy_total",
            )
        )
        df = pd.DataFrame(
            {
                "tiempo_s": data["time"][:n],
                "log10_divergencia": data["div"][:n],
                "theta1_rad": data["phase_x"][:n],
                "theta2_rad": data["phase_y"][:n],
                "energia_cinetica_J": data["energy_t"][:n],
                "energia_potencial_J": data["energy_v"][:n],
                "energia_total_J": data["energy_total"][:n],
            }
        )
        return dcc.send_data_frame(
            df.to_csv, "mediciones_pendulo_doble.csv", index=False
        )
