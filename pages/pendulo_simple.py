"""Módulo de página: Simulador interactivo de Péndulo Simple N-Cuerpo (Diseño compacto 1 pantalla).

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
.pd-app-container .action-btn:hover{{background:var(--btn-bg);
color:var(--accent); border-color:var(--accent)}}
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
    gap:8px 16px;align-content:space-between;
}}
.pd-app-container .slider-group{{min-width:0}}
.pd-app-container .slider-group.full-span{{grid-column:1 / -1}}
.pd-app-container .slider-header{{
    display:flex;justify-content:space-between;align-items:center;
    gap:6px;font-size:11.5px;color:var(--text-muted);margin-bottom:4px;
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
    padding:6px 16px;border-radius:6px 20px 20px 6px;cursor:pointer;
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
    {"name": "Vel. Angular ω₁ (rad/s)", "id": "fase_y"},
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


def crear_modal_conceptos_simple():
    """Construye la ventana emergente con las 3 pestañas de conceptos del Péndulo Simple en LaTeX."""
    return html.Div(
        id="ps-modal-overlay",
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
                                        "¿Qué es el péndulo simple?",
                                        id="ps-tab-modal-fisico",
                                        n_clicks=0,
                                        className="pd-modal-tab active",
                                    ),
                                    html.Button(
                                        "Modelo matemático",
                                        id="ps-tab-modal-modelo",
                                        n_clicks=0,
                                        className="pd-modal-tab",
                                    ),
                                    html.Button(
                                        "Análisis del sistema",
                                        id="ps-tab-modal-analisis",
                                        n_clicks=0,
                                        className="pd-modal-tab",
                                    ),
                                ],
                            ),
                            html.Button(
                                "✕",
                                id="ps-btn-modal-cerrar",
                                n_clicks=0,
                                className="pd-modal-close",
                                title="Cerrar",
                            ),
                        ],
                    ),
                    # Contenido 1: ¿Qué es el péndulo simple? / Supuestos y Período
                    html.Div(
                        id="ps-modal-body-fisico",
                        className="pd-modal-body",
                        style={"display": "block"},
                        children=[
                            dcc.Markdown(
                                r"""
### ¿Qué es el Péndulo Simple?
El **péndulo simple** es un sistema mecánico idealizado de un único grado de libertad cuya [variedad de configuración](https://es.wikipedia.org/wiki/Espacio_de_configuraci%C3%B3n) es el círculo unitario $Q = S^1$. Consiste en una masa puntual $m_1$ suspendida de un pivote fijo mediante una varilla rígida e inextensible de longitud $L_1$ y masa despreciable, sometida a un campo gravitacional uniforme $g$ y a un coeficiente de amortiguamiento viscoso $b$.

En coordenadas cartesianas respecto al pivote, la posición y rapidez instantáneas de la partícula quedan restringidas a la circunferencia de radio $L_1$:
                                """,
                                mathjax=True,
                                link_target="_blank",
                            ),
                            html.Div(
                                className="pd-formula-box",
                                children=[
                                    dcc.Markdown(
                                        r"$$x(t) = L_1 \sin\theta_1(t), \qquad y(t) = -L_1 \cos\theta_1(t), \qquad v(t) = L_1 |\dot{\theta}_1(t)|$$",
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
#### Supuestos físicos e idealizaciones
* **Masa puntual ajustable:** Toda la inercia reside en la esfera de masa $m_1$ ($0.2\text{ a }5.0\text{ kg}$), con momento de inercia $I = m_1 L_1^2$. Por equivalencia gravitatoria-inercial, el período libre no depende de $m_1$, pero la energía mecánica total escala linealmente con ella.
* **Vínculo holónomo rígido:** La barra no experimenta flexión ni elongación elástica ($r(t) \equiv L_1$).
* **Disipación lineal:** El medio produce una desaceleración viscosa proporcional a la velocidad angular $\omega_1 = \dot{\theta}_1$.
* **Ensamble $N$-cuerpo:** Se integran en paralelo $N$ copias independientes con perturbaciones iniciales $\theta_1^{(k)}(0) = \theta_1(0) + k\Delta\theta_0$.
                                            """,
                                            mathjax=True,
                                            link_target="_blank",
                                        ),
                                    ),
                                    html.Div(
                                        className="pd-concept-box",
                                        children=dcc.Markdown(
                                            r"""
#### Régimen lineal vs. No lineal (Anarmonicidad)
* **Ángulos pequeños ($|\theta_1| \ll 1\text{ rad}$):** Mediante el desarrollo de Taylor $\sin\theta_1 \approx \theta_1 - \frac{1}{6}\theta_1^3$, el sistema se reduce a un [oscilador armónico](https://es.wikipedia.org/wiki/Oscilador_arm%C3%B3nico) con frecuencia natural $\omega_0 = \sqrt{g/L_1}$ y período isócrono $T_0 = 2\pi\sqrt{L_1/g}$.
* **Grandes amplitudes:** La fuerza restauradora crece más lento que $\theta_1$ y el período exacto depende de la amplitud inicial $\theta_0$ mediante la integral elíptica completa de primera especie $K(k)$, con $k = \sin(\theta_0/2)$:
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
                                        r"$$T(\theta_0) = 4\sqrt{\frac{L_1}{g}}\int_0^{\pi/2}\frac{d\phi}{\sqrt{1 - \sin^2(\theta_0/2)\sin^2\phi}} = T_0\left(1 + \frac{1}{16}\theta_0^2 + \frac{11}{3072}\theta_0^4 + \mathcal{O}(\theta_0^6)\right)$$",
                                        mathjax=True,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Contenido 2: Modelo matemático
                    html.Div(
                        id="ps-modal-body-modelo",
                        className="pd-modal-body",
                        style={"display": "none"},
                        children=[
                            dcc.Markdown(
                                r"""
### Modelo Matemático y Formulación Lagrangiana
Definimos la energía cinética $T(\dot{\theta}_1)$, la energía potencial gravitatoria $V(\theta_1)$ (tomando $V=0$ en el equilibrio inferior $\theta_1 = 0$), el [Lagrangiano](https://es.wikipedia.org/wiki/Lagrangiano) $\mathcal{L} = T - V$ y la [función de disipación de Rayleigh](https://en.wikipedia.org/wiki/Rayleigh_dissipation_function) $\mathcal{R}(\dot{\theta}_1)$:
                                """,
                                mathjax=True,
                                link_target="_blank",
                            ),
                            html.Div(
                                className="pd-formula-box",
                                children=[
                                    dcc.Markdown(
                                        r"$$\mathcal{L}(\theta_1, \dot{\theta}_1) = \frac{1}{2}m_1 L_1^2 \dot{\theta}_1^2 - m_1 g L_1 (1 - \cos\theta_1), \qquad \mathcal{R}(\dot{\theta}_1) = \frac{1}{2}b m_1 L_1^2 \dot{\theta}_1^2$$",
                                        mathjax=True,
                                    ),
                                ],
                            ),
                            dcc.Markdown(
                                r"""
Aplicando la [ecuación de Euler-Lagrange](https://es.wikipedia.org/wiki/Ecuaciones_de_Euler-Lagrange) con fuerzas disipativas generalizadas se obtiene la ecuación diferencial ordinaria no lineal de segundo orden:
                                """,
                                mathjax=True,
                                link_target="_blank",
                            ),
                            html.Div(
                                className="pd-formula-box",
                                children=[
                                    dcc.Markdown(
                                        r"$$\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{\theta}_1}\right) - \frac{\partial \mathcal{L}}{\partial \theta_1} + \frac{\partial \mathcal{R}}{\partial \dot{\theta}_1} = 0 \quad \Longrightarrow \quad \ddot{\theta}_1(t) + b\dot{\theta}_1(t) + \frac{g}{L_1}\sin\theta_1(t) = 0$$",
                                        mathjax=True,
                                    ),
                                ],
                            ),
                            html.Div(
                                className="pd-concept-grid",
                                children=[
                                    html.Div(
                                        className="pd-concept-box",
                                        children=[
                                            dcc.Markdown(
                                                r"""
#### Sistema autónomo en el espacio de estados
Introduciendo el vector de estado $x = (\theta_1, \omega_1)^\top \in S^1 \times \mathbb{R}$, la ecuación de segundo orden equivale al campo vectorial suave $\dot{x} = F(x)$:
                                                """,
                                                mathjax=True,
                                            ),
                                            dcc.Markdown(
                                                r"$$\dot{\theta}_1 = \omega_1, \qquad \dot{\omega}_1 = -\frac{g}{L_1}\sin\theta_1 - b\omega_1$$",
                                                mathjax=True,
                                            ),
                                            dcc.Markdown(
                                                r"El motor numérico avanza con paso $\Delta t = 10^{-3}\text{ s}$ mediante **Runge-Kutta de 4.º orden (RK4)** con error global $\mathcal{O}(\Delta t^4)$.",
                                                mathjax=True,
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="pd-concept-box",
                                        children=[
                                            dcc.Markdown(
                                                r"""
#### Balance de energía mecánica
La energía mecánica total instantánea y su tasa de disipación a lo largo de las trayectorias son:
                                                """,
                                                mathjax=True,
                                            ),
                                            dcc.Markdown(
                                                r"$$E(\theta_1, \omega_1) = \frac{1}{2}m_1 L_1^2 \omega_1^2 + m_1 g L_1(1 - \cos\theta_1)$$",
                                                mathjax=True,
                                            ),
                                            dcc.Markdown(
                                                r"$$\frac{dE}{dt} = \nabla E \cdot F(x) = -b m_1 L_1^2 \omega_1^2 \le 0$$",
                                                mathjax=True,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Contenido 3: Análisis del sistema
                    html.Div(
                        id="ps-modal-body-analisis",
                        className="pd-modal-body",
                        style={"display": "none"},
                        children=[
                            dcc.Markdown(
                                r"""
### Análisis Cualitativo, Estabilidad y Espacio de Fases
Los puntos de equilibrio satisfacen $F(\theta_1^*, \omega_1^*) = (0,0)^\top$, lo que implica $\omega_1^* = 0$ y $\sin\theta_1^* = 0$. La estabilidad local se determina mediante la traza, el determinante y el polinomio característico de la matriz Jacobiana $J = DF(\theta_1, \omega_1)$:
                                """,
                                mathjax=True,
                                link_target="_blank",
                            ),
                            html.Div(
                                className="pd-formula-box",
                                children=[
                                    dcc.Markdown(
                                        r"$$\operatorname{tr}(J) = -b, \qquad \det(J) = \frac{g}{L_1}\cos\theta_1, \qquad P(\lambda) = \lambda^2 + b\lambda + \frac{g}{L_1}\cos\theta_1 = 0$$",
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
#### Clasificación de Puntos de Equilibrio
* **Equilibrio inferior $x_s = (0, 0)$:** Mínimo de potencial ($E = 0$) con autovalores $\lambda_{\pm} = \frac{1}{2}\left(-b \pm \sqrt{b^2 - 4\omega_0^2}\right)$:
  1. Si $b = 0$: $\lambda_{\pm} = \pm i\omega_0$ (**centro no lineal** Lyapunov-estable rodeado de órbitas periódicas).
  2. Si $0 < b < 2\omega_0$: **foco espiral asintóticamente estable** (régimen subamortiguado).
  3. Si $b \ge 2\omega_0$: **nodo asintóticamente estable** (régimen sobreamortiguado).
* **Equilibrio invertido $x_u = (\pm\pi, 0)$:** Máximo de potencial ($E = 2m_1 g L_1$) con $\det(J) = -\omega_0^2 < 0$ y autovalores reales $\lambda_- < 0 < \lambda_+$, formando un **punto de silla hiperbólico** inestable.
                                            """,
                                            mathjax=True,
                                            link_target="_blank",
                                        ),
                                    ),
                                    html.Div(
                                        className="pd-concept-box",
                                        children=[
                                            dcc.Markdown(
                                                r"""
#### Topología del Retrato de Fases y Ausencia de Caos
* **Libración ($E < 2m_1 g L_1$):** Órbitas cerradas acotadas donde el péndulo oscila entre $[-\theta_{\max}, \theta_{\max}]$.
* **Separatriz heteroclínica ($E = 2m_1 g L_1$):** Curva invariante que conecta las sillas $(-\pi, 0)$ y $(\pi, 0)$ en tiempo infinito:
                                                """,
                                                mathjax=True,
                                            ),
                                            dcc.Markdown(
                                                r"$$\omega_1(\theta_1) = \pm 2\sqrt{\frac{g}{L_1}}\cos\left(\frac{\theta_1}{2}\right)$$",
                                                mathjax=True,
                                            ),
                                            dcc.Markdown(
                                                r"""
* [**Teorema de Poincaré-Bendixson**](https://en.wikipedia.org/wiki/Poincar%C3%A9%E2%80%93Bendixson_theorem): En un flujo autónomo bidimensional ($S^1 \times \mathbb{R}$) no existen atractores extraños. Por tanto, **el péndulo simple es integrable y no puede exhibir caos determinista** ($\lambda_{\max} = 0$).
                                                """,
                                                mathjax=True,
                                                link_target="_blank",
                                            ),
                                        ],
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
            dcc.Store(id="ps-client-sync", data=0),
            dcc.Store(id="ps-analysis-store", data=None),
            dcc.Download(id="ps-download-csv"),
            # Ventana emergente de conceptos (oculta por defecto con opacidad 0)
            crear_modal_conceptos_simple(),
            # Cabecera + Botones emergentes de conceptos + Pestañas en una sola línea
            html.Div(
                className="header-bar",
                children=[
                    html.Div(
                        [
                            html.H1("Simulador Interactivo de Péndulo Simple N-Cuerpo"),
                            html.Div(
                                "Oscilaciones periódicas, espacio de fases (θ₁ vs ω₁) y amortiguamiento mediante RK4",
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
                                        "¿Qué es el péndulo simple?",
                                        id="ps-btn-modal-fisico",
                                        n_clicks=0,
                                        className="concept-btn",
                                    ),
                                    html.Button(
                                        "Modelo matemático",
                                        id="ps-btn-modal-modelo",
                                        n_clicks=0,
                                        className="concept-btn",
                                    ),
                                    html.Button(
                                        "Análisis del sistema",
                                        id="ps-btn-modal-analisis",
                                        n_clicks=0,
                                        className="concept-btn",
                                    ),
                                ],
                            ),
                            dcc.Tabs(
                                id="ps-tabs-navigation",
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
                id="ps-panel-simulador",
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
                                            html.Span("0.000 s", id="ps-ind-time"),
                                        ],
                                    ),
                                    html.Div(
                                        className="pill",
                                        children=[
                                            "Δθ máx: ",
                                            html.Span("0.00e+0 rad", id="ps-ind-div"),
                                        ],
                                    ),
                                    html.Div(
                                        className="pill",
                                        children=[
                                            "Energía E: ",
                                            html.Span("0.00 J", id="ps-ind-energy"),
                                        ],
                                    ),
                                    html.Div(
                                        className="pill",
                                        children=[
                                            "FPS: ",
                                            html.Span("—", id="ps-ind-fps"),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(
                                className="action-row",
                                children=[
                                    html.Button(
                                        "Iniciar",
                                        id="ps-btn-iniciar",
                                        n_clicks=0,
                                        className="action-btn primary",
                                    ),
                                    html.Button(
                                        "Reiniciar a t=0",
                                        id="ps-btn-reiniciar",
                                        n_clicks=0,
                                        className="action-btn",
                                    ),
                                    html.Button(
                                        "Limpiar Estelas",
                                        id="ps-btn-limpiar",
                                        n_clicks=0,
                                        className="action-btn",
                                    ),
                                    html.Button(
                                        "Fijar Estelas",
                                        id="ps-btn-fijar",
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
                                        "VISTA FÍSICA (PÉNDULO SIMPLE)",
                                        id="ps-title-fisica",
                                        className="panel-title",
                                    ),
                                    html.Div(
                                        id="ps-canvas-physics-host",
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
                                                id="ps-canvas-div-host",
                                                className="canvas-host canvas-chart-size",
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="panel",
                                        children=[
                                            html.Div(
                                                "ESPACIO DE FASES (θ₁ vs ω₁)",
                                                id="ps-title-fase",
                                                className="panel-title",
                                            ),
                                            html.Div(
                                                id="ps-canvas-phase-host",
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
                                        "ps-sl-t1",
                                        -180,
                                        180,
                                        1,
                                        120,
                                        "ps-val-t1",
                                        "120°",
                                    ),
                                    slider(
                                        "N.º péndulos (N)",
                                        "ps-sl-n",
                                        1,
                                        12,
                                        1,
                                        5,
                                        "ps-val-n",
                                        "5",
                                    ),
                                    slider(
                                        "Perturbación log₁₀(Δθ₀)",
                                        "ps-sl-dt",
                                        -6,
                                        0,
                                        0.1,
                                        -3,
                                        "ps-val-dt",
                                        "-3.0",
                                    ),
                                    slider(
                                        "Longitud L₁ (m)",
                                        "ps-sl-l1",
                                        0.5,
                                        3,
                                        0.1,
                                        2,
                                        "ps-val-l1",
                                        "2.0 m",
                                    ),
                                    slider(
                                        "Gravedad g (m/s²)",
                                        "ps-sl-g",
                                        0,
                                        25,
                                        0.1,
                                        9.8,
                                        "ps-val-g",
                                        "9.8 m/s²",
                                    ),
                                    slider(
                                        "Amortiguamiento b (s⁻¹)",
                                        "ps-sl-b",
                                        0,
                                        0.5,
                                        0.01,
                                        0,
                                        "ps-val-b",
                                        "0.00",
                                    ),
                                    slider(
                                        "Masa m₁ (kg)",
                                        "ps-sl-m1",
                                        0.2,
                                        5.0,
                                        0.1,
                                        1.0,
                                        "ps-val-m1",
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
                                                                id="ps-val-speed",
                                                                className="val",
                                                            ),
                                                            html.Button(
                                                                "x0.5",
                                                                id="ps-btn-half",
                                                                n_clicks=0,
                                                                className="btn-small",
                                                            ),
                                                            html.Button(
                                                                "x2",
                                                                id="ps-btn-x2",
                                                                n_clicks=0,
                                                                className="btn-small",
                                                            ),
                                                            html.Button(
                                                                "↺",
                                                                id="ps-btn-reset-speed",
                                                                n_clicks=0,
                                                                className="btn-small",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            ),
                                            dcc.Slider(
                                                id="ps-sl-speed",
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
                    # Botón inferior izquierdo para ir inmediatamente a Péndulo Doble
                    html.Div(
                        className="switch-lab-row",
                        children=[
                            html.Button(
                                "Péndulo doble ▶",
                                id="ps-btn-ir-doble",
                                n_clicks=0,
                                className="switch-lab-btn",
                                title="Ir al simulador de Péndulo Doble",
                            ),
                        ],
                    ),
                ],
            ),
            # CONTENEDOR PERSISTENTE 2: MEDICIONES Y GUÍA TEÓRICA
            html.Div(
                id="ps-panel-datos",
                style={"display": "none"},
                children=[
                    html.Div(
                        className="info-card",
                        children=[
                            html.H3("Motivación, supuestos y uso (Péndulo Simple)"),
                            dcc.Markdown(
                                r"""
El péndulo simple ideal consta de una masa puntual $m_1$ suspendida de un hilo inextensible de longitud $L_1$ sin masa. Su ecuación diferencial de movimiento es $\ddot{\theta}_1 + b\dot{\theta}_1 + (g/L_1)\sin\theta_1 = 0$.

Por poseer un único grado de libertad (espacio de fases bidimensional $\theta_1$ vs $\omega_1$), el [**Teorema de Poincaré-Bendixson**](https://en.wikipedia.org/wiki/Poincar%C3%A9%E2%80%93Bendixson_theorem) garantiza que este sistema autónomo es integrable y no puede presentar caos: sus trayectorias forman órbitas cerradas periódicas (si $b=0$) o espirales convergentes hacia el equilibrio estable (si $b>0$).
                                """,
                                mathjax=True,
                                link_target="_blank",
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
                                        id="ps-btn-capturar",
                                        n_clicks=0,
                                        className="action-btn primary",
                                    ),
                                    html.Button(
                                        "⬇ Descargar CSV",
                                        id="ps-btn-download-csv",
                                        n_clicks=0,
                                        className="action-btn",
                                    ),
                                    html.Span(
                                        id="ps-analysis-status",
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
                                "REGISTRO HISTÓRICO DE LA CAPTURA (PÉNDULO SIMPLE)",
                                className="panel-title",
                            ),
                            dash_table.DataTable(
                                id="ps-tabla-mediciones",
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
    if "</head>" in app.index_string and "ps-scoped-styles" not in app.index_string:
        app.index_string = app.index_string.replace(
            "</head>", f'<style id="ps-scoped-styles">{CSS}</style></head>'
        )

    # Transición inmediata hacia Péndulo Doble
    app.clientside_callback(
        """function(nClicks) {
            if (!nClicks) return window.dash_clientside.no_update;
            const navBtn = document.getElementById('sd-nav-pendulo_doble');
            if (navBtn) navBtn.click();
            return window.dash_clientside.no_update;
        }""",
        Output("ps-btn-ir-doble", "n_clicks"),
        Input("ps-btn-ir-doble", "n_clicks"),
        prevent_initial_call=True,
    )

    # Control animado de las pestañas emergentes
    app.clientside_callback(
        """function(bFis, bMod, bAna, tFis, tMod, tAna, bClose) {
            const trig = window.dash_clientside.callback_context.triggered_id;
            const prevIdx = (typeof window._psModalTabIdx === 'number') ? window._psModalTabIdx : 0;
            const wasOpen = Boolean(window._psModalOpen);

            if (!trig || trig === 'ps-btn-modal-cerrar') {
                window._psModalOpen = false;
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
            if (trig === 'ps-btn-modal-fisico' || trig === 'ps-tab-modal-fisico') targetIdx = 0;
            else if (trig === 'ps-btn-modal-modelo' || trig === 'ps-tab-modal-modelo') targetIdx = 1;
            else if (trig === 'ps-btn-modal-analisis' || trig === 'ps-tab-modal-analisis') targetIdx = 2;

            let animClass = 'pd-modal-body anim-emerge';
            if (wasOpen && targetIdx !== prevIdx) {
                animClass = (targetIdx > prevIdx) ? 'pd-modal-body anim-right' : 'pd-modal-body anim-left';
            }

            window._psModalOpen = true;
            window._psModalTabIdx = targetIdx;

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
        Output("ps-modal-overlay", "className"),
        Output("ps-modal-body-fisico", "style"),
        Output("ps-modal-body-modelo", "style"),
        Output("ps-modal-body-analisis", "style"),
        Output("ps-modal-body-fisico", "className"),
        Output("ps-modal-body-modelo", "className"),
        Output("ps-modal-body-analisis", "className"),
        Output("ps-tab-modal-fisico", "className"),
        Output("ps-tab-modal-modelo", "className"),
        Output("ps-tab-modal-analisis", "className"),
        Input("ps-btn-modal-fisico", "n_clicks"),
        Input("ps-btn-modal-modelo", "n_clicks"),
        Input("ps-btn-modal-analisis", "n_clicks"),
        Input("ps-tab-modal-fisico", "n_clicks"),
        Input("ps-tab-modal-modelo", "n_clicks"),
        Input("ps-tab-modal-analisis", "n_clicks"),
        Input("ps-btn-modal-cerrar", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """function(tabValue) {
            if (tabValue === 'tab-datos') {
                return [{display: 'none'}, {display: 'block'}];
            }
            setTimeout(function() {
                if (window.PendulumSimpleApp && typeof window.PendulumSimpleApp.refreshView === 'function') {
                    window.PendulumSimpleApp.refreshView();
                }
            }, 30);
            return [{display: 'block'}, {display: 'none'}];
        }""",
        Output("ps-panel-simulador", "style"),
        Output("ps-panel-datos", "style"),
        Input("ps-tabs-navigation", "value"),
    )

    app.clientside_callback(
        """function(t1,n,logdt,l1,g,b,m1,speed,cStart,cReset,cClear,cFix) {
            if (!window.PendulumSimpleApp) return window.dash_clientside.no_update;
            window.PendulumSimpleApp.sync({t1,t2:0,n,logdt,l1,l2:1.0,g,b,m1,m2:1.0,speed,cStart,cReset,cClear,cFix});
            return (window.PendulumSimpleApp.syncCount || 0);
        }""",
        Output("ps-client-sync", "data"),
        Input("ps-sl-t1", "value"),
        Input("ps-sl-n", "value"),
        Input("ps-sl-dt", "value"),
        Input("ps-sl-l1", "value"),
        Input("ps-sl-g", "value"),
        Input("ps-sl-b", "value"),
        Input("ps-sl-m1", "value"),
        Input("ps-sl-speed", "value"),
        Input("ps-btn-iniciar", "n_clicks"),
        Input("ps-btn-reiniciar", "n_clicks"),
        Input("ps-btn-limpiar", "n_clicks"),
        Input("ps-btn-fijar", "n_clicks"),
    )

    app.clientside_callback(
        """function(nHalf,nDouble,nReset,current,maxValue) {
            const triggered = window.dash_clientside.callback_context.triggered_id;
            if (!triggered) return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            let value = Number(current), max = Number(maxValue);
            if (triggered === 'ps-btn-half') value = Math.max(0.1, value * 0.5);
            else if (triggered === 'ps-btn-x2') { value = value * 2; max = Math.max(max, value); }
            else if (triggered === 'ps-btn-reset-speed') { value = 1; max = 10; }
            else return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            value = Math.round(value * 10) / 10;
            return [value, max];
        }""",
        Output("ps-sl-speed", "value"),
        Output("ps-sl-speed", "max"),
        Input("ps-btn-half", "n_clicks"),
        Input("ps-btn-x2", "n_clicks"),
        Input("ps-btn-reset-speed", "n_clicks"),
        State("ps-sl-speed", "value"),
        State("ps-sl-speed", "max"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """function(nClicks, tabValue) {
            if (!window.PendulumSimpleApp) return window.dash_clientside.no_update;
            const triggered = window.dash_clientside.callback_context.triggered_id;
            if (triggered === 'ps-tabs-navigation' && tabValue !== 'tab-datos') {
                return window.dash_clientside.no_update;
            }
            return window.PendulumSimpleApp.snapshot();
        }""",
        Output("ps-analysis-store", "data"),
        Input("ps-btn-capturar", "n_clicks"),
        Input("ps-tabs-navigation", "value"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output("ps-tabla-mediciones", "data"),
        Output("ps-analysis-status", "children"),
        Input("ps-analysis-store", "data"),
    )
    def update_table_simple(data):
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
        Output("ps-download-csv", "data"),
        Input("ps-btn-download-csv", "n_clicks"),
        State("ps-analysis-store", "data"),
        prevent_initial_call=True,
    )
    def download_csv_simple(_clicks, data):
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
                "omega1_rad_s": data["phase_y"][:n],
                "energia_cinetica_J": data["energy_t"][:n],
                "energia_potencial_J": data["energy_v"][:n],
                "energia_total_J": data["energy_total"][:n],
            }
        )
        return dcc.send_data_frame(
            df.to_csv, "mediciones_pendulo_simple.csv", index=False
        )
