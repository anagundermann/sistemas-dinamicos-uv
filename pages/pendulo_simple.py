"""Módulo de página: Simulador interactivo de Péndulo Simple N-Cuerpo (Diseño compacto 1 pantalla).

Diseñado para integrarse en la arquitectura multipágina de Sistemas Dinámicos UV.
Expone `crear_pagina()` y `registrar_callbacks(app)`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dash import Input, Output, State, dash_table, dcc, html

BG = "#FFFFFF"
PANEL = "#c3c3ca"
BORDER = "#000000"
TEXT = "#000000"
MUTED = "#000000"
ACCENT = "#be00eefc"

CSS = f"""
.pd-app-container{{
    --bg-body:{BG};--bg-panel:{PANEL};--border:{BORDER};
    --text-main:{TEXT};--text-muted:{MUTED};--accent:{ACCENT};--btn-bg:#2a2a32;
    background:var(--bg-body);color:var(--text-main);
    font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
    padding:14px 18px;border-radius:14px;width:100%;max-width:1500px;margin:auto;
    box-sizing:border-box;
}}
.pd-app-container *{{box-sizing:border-box}}
.pd-app-container .header-bar{{
    display:flex;justify-content:space-between;align-items:center;
    gap:16px;flex-wrap:wrap;margin-bottom:10px;border-bottom:1px solid var(--border);
    padding-bottom:8px;
}}
.pd-app-container h1{{font-size:19px;font-weight:600;margin:0;color:var(--text-main)}}
.pd-app-container .subtitle{{color:var(--text-muted);font-size:12px;margin:2px 0 0}}
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
    background:var(--bg-panel);border:1px solid var(--border);color:var(--text-main);
    padding:5px 14px;border-radius:18px;cursor:pointer;font-size:12px;transition:.15s;
}}
.pd-app-container .action-btn:hover{{background:var(--btn-bg)}}
.pd-app-container .action-btn.primary{{border-color:var(--text-main)}}
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
    background:var(--bg-panel);border:1px solid var(--border);
    border-radius:10px;padding:10px 12px;min-width:0;
}}
.pd-app-container .panel-title{{
    font-size:10px;text-transform:uppercase;letter-spacing:0.8px;
    color:var(--text-muted);margin-bottom:6px;
}}
.pd-app-container .canvas-host{{position:relative;width:100%}}
.pd-app-container .canvas-host canvas{{display:block;width:100%;height:100%}}
.pd-app-container .canvas-physics-size{{height:350px;min-height:280px}}
.pd-app-container .canvas-chart-size{{height:156px;min-height:130px}}

/* Panel de Sliders compacto a la derecha */
.pd-app-container .sliders-panel{{
    background:var(--bg-panel);border:1px solid var(--border);
    border-radius:10px;padding:12px 14px;
    display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
    gap:12px 16px;align-content:space-between;
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
.pd-app-container .info-card h3{{margin:0 0 6px;color:var(--accent);font-size:16px}}
.pd-app-container .note{{color:var(--text-muted);font-size:11px;line-height:1.4}}
@media(max-width:1100px){{
    .pd-app-container .workspace-grid{{grid-template-columns:1fr 1fr}}
    .pd-app-container .sliders-panel{{grid-column:1 / -1;grid-template-columns:repeat(3,minmax(0,1fr))}}
}}
@media(max-width:720px){{
    .pd-app-container .workspace-grid{{grid-template-columns:1fr}}
    .pd-app-container .sliders-panel{{grid-template-columns:1fr}}
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


def slider(label, sid, minimum, maximum, step, value, value_id, display, full_span=False):
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


def crear_pagina():
    return html.Div(
        className="pd-app-container",
        children=[
            dcc.Store(id="ps-client-sync", data=0),
            dcc.Store(id="ps-analysis-store", data=None),
            dcc.Download(id="ps-download-csv"),
            # Cabecera + Pestañas en una sola línea
            html.Div(
                className="header-bar",
                children=[
                    html.Div([
                        html.H1("Simulador Interactivo de Péndulo Simple N-Cuerpo"),
                        html.Div(
                            "Oscilaciones periódicas, espacio de fases (θ₁ vs ω₁) y amortiguamiento mediante RK4",
                            className="subtitle",
                        ),
                    ]),
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
            # CONTENEDOR PERSISTENTE 1: SIMULADOR COMPACTO EN 1 PANTALLA
            html.Div(
                id="ps-panel-simulador",
                style={"display": "block"},
                children=[
                    # Barra unificada: Indicadores a la izquierda, Botones a la derecha
                    html.Div(
                        className="top-controls",
                        children=[
                            html.Div(
                                className="indicators",
                                children=[
                                    html.Div(className="pill", children=["Tiempo t: ", html.Span("0.000 s", id="ps-ind-time")]),
                                    html.Div(className="pill", children=["Δθ máx: ", html.Span("0.00e+0 rad", id="ps-ind-div")]),
                                    html.Div(className="pill", children=["Energía E: ", html.Span("0.00 J", id="ps-ind-energy")]),
                                    html.Div(className="pill", children=["FPS: ", html.Span("—", id="ps-ind-fps")]),
                                ],
                            ),
                            html.Div(
                                className="action-row",
                                children=[
                                    html.Button("Iniciar", id="ps-btn-iniciar", n_clicks=0, className="action-btn primary"),
                                    html.Button("Reiniciar a t=0", id="ps-btn-reiniciar", n_clicks=0, className="action-btn"),
                                    html.Button("Limpiar Estelas", id="ps-btn-limpiar", n_clicks=0, className="action-btn"),
                                    html.Button("Fijar Estelas", id="ps-btn-fijar", n_clicks=0, className="action-btn"),
                                ],
                            ),
                        ],
                    ),
                    # Espacio de trabajo en 3 columnas: Vista Física | Gráficas | Sliders
                    html.Div(
                        className="workspace-grid",
                        children=[
                            # Columna 1: Vista física
                            html.Div(
                                className="panel",
                                children=[
                                    html.Div("VISTA FÍSICA (PÉNDULO SIMPLE)", id="ps-title-fisica", className="panel-title"),
                                    html.Div(id="ps-canvas-physics-host", className="canvas-host canvas-physics-size"),
                                ],
                            ),
                            # Columna 2: Divergencia y Espacio de Fases
                            html.Div(
                                className="right-column",
                                children=[
                                    html.Div(
                                        className="panel",
                                        children=[
                                            html.Div("DIVERGENCIA DE TRAYECTORIAS log₁₀(Δθ)", className="panel-title"),
                                            html.Div(id="ps-canvas-div-host", className="canvas-host canvas-chart-size"),
                                        ],
                                    ),
                                    html.Div(
                                        className="panel",
                                        children=[
                                            html.Div("ESPACIO DE FASES (θ₁ vs ω₁)", id="ps-title-fase", className="panel-title"),
                                            html.Div(id="ps-canvas-phase-host", className="canvas-host canvas-chart-size"),
                                        ],
                                    ),
                                ],
                            ),
                            # Columna 3: Panel de Parámetros (Sliders)
                            html.Div(
                                className="sliders-panel",
                                children=[
                                    slider("θ₁ Inicial (°)", "ps-sl-t1", -180, 180, 1, 120, "ps-val-t1", "120°"),
                                    slider("N.º péndulos (N)", "ps-sl-n", 1, 12, 1, 5, "ps-val-n", "5"),
                                    slider("Perturbación log₁₀(Δθ₀)", "ps-sl-dt", -6, 0, 0.1, -3, "ps-val-dt", "-3.0"),
                                    slider("Longitud L₁ (m)", "ps-sl-l1", 0.5, 3, 0.1, 2, "ps-val-l1", "2.0 m"),
                                    slider("Gravedad g (m/s²)", "ps-sl-g", 0, 25, 0.1, 9.8, "ps-val-g", "9.8 m/s²"),
                                    slider("Amortiguamiento b (s⁻¹)", "ps-sl-b", 0, 0.5, 0.01, 0, "ps-val-b", "0.00"),
                                    html.Div(
                                        className="slider-group full-span",
                                        children=[
                                            html.Div(
                                                className="slider-header",
                                                children=[
                                                    html.Span("Velocidad de simulación"),
                                                    html.Div(
                                                        className="speed-buttons",
                                                        children=[
                                                            html.Span("1.0x", id="ps-val-speed", className="val"),
                                                            html.Button("x0.5", id="ps-btn-half", n_clicks=0, className="btn-small"),
                                                            html.Button("x2", id="ps-btn-x2", n_clicks=0, className="btn-small"),
                                                            html.Button("↺", id="ps-btn-reset-speed", n_clicks=0, className="btn-small"),
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
                            html.P("El péndulo simple ideal consta de una masa puntual m₁ suspendida de un hilo inextensible de longitud L₁ sin masa. Su ecuación diferencial es θ̈₁ + bθ̇₁ + (g/L₁)sin(θ₁) = 0."),
                            html.P("Por tener un único grado de libertad (espacio de fases bidimensional θ₁ vs ω₁), el Teorema de Poincaré-Bendixson garantiza que este sistema autónomo es integrable y no puede presentar caos: sus trayectorias forman órbitas cerradas periódicas (si b=0) o espirales convergentes hacia el equilibrio estable (si b>0)."),
                            html.Div(
                                style={"marginTop": "12px", "display": "flex", "gap": "10px", "alignItems": "center", "flexWrap": "wrap"},
                                children=[
                                    html.Button("Actualizar tabla con estado actual", id="ps-btn-capturar", n_clicks=0, className="action-btn primary"),
                                    html.Button("⬇ Descargar CSV", id="ps-btn-download-csv", n_clicks=0, className="action-btn"),
                                    html.Span(id="ps-analysis-status", className="note", style={"marginLeft": "10px"}),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="panel",
                        children=[
                            html.Div("REGISTRO HISTÓRICO DE LA CAPTURA (PÉNDULO SIMPLE)", className="panel-title"),
                            dash_table.DataTable(
                                id="ps-tabla-mediciones",
                                columns=initial_table_columns,
                                data=[],
                                page_size=10,
                                style_table={"overflowX": "auto"},
                                style_header={"backgroundColor": "#25252d", "color": ACCENT, "fontWeight": "bold", "border": f"1px solid {BORDER}"},
                                style_cell={"backgroundColor": PANEL, "color": TEXT, "border": f"1px solid {BORDER}", "fontFamily": "monospace", "textAlign": "center", "padding": "6px", "minWidth": "100px"},
                                style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#202027"}],
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
        """function(t1,n,logdt,l1,g,b,speed,cStart,cReset,cClear,cFix) {
            if (!window.PendulumSimpleApp) return window.dash_clientside.no_update;
            window.PendulumSimpleApp.sync({t1,t2:0,n,logdt,l1,l2:1.0,g,b,speed,cStart,cReset,cClear,cFix});
            return (window.PendulumSimpleApp.syncCount || 0);
        }""",
        Output("ps-client-sync", "data"),
        Input("ps-sl-t1", "value"),
        Input("ps-sl-n", "value"),
        Input("ps-sl-dt", "value"),
        Input("ps-sl-l1", "value"),
        Input("ps-sl-g", "value"),
        Input("ps-sl-b", "value"),
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

        rows = [{
            "tiempo": round(float(ti), 6), "divergencia": round(float(di), 8),
            "fase_x": round(float(xi), 8), "fase_y": round(float(yi), 8),
            "energia_cinetica": round(float(kti), 8), "energia_potencial": round(float(kvi), 8),
            "energia_total": round(float(kei), 8),
        } for ti, di, xi, yi, kti, kvi, kei in zip(t, div, px, py, et, ev, ee)][::-1]

        status = f"Captura actualizada: {n} muestras registradas (hasta t = {t[-1]:.3f} s)."
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
        n = min(len(data.get(k, [])) for k in ("time", "div", "phase_x", "phase_y", "energy_t", "energy_v", "energy_total"))
        df = pd.DataFrame({
            "tiempo_s": data["time"][:n], "log10_divergencia": data["div"][:n],
            "theta1_rad": data["phase_x"][:n], "omega1_rad_s": data["phase_y"][:n],
            "energia_cinetica_J": data["energy_t"][:n],
            "energia_potencial_J": data["energy_v"][:n],
            "energia_total_J": data["energy_total"][:n],
        })
        return dcc.send_data_frame(df.to_csv, "mediciones_pendulo_simple.csv", index=False)