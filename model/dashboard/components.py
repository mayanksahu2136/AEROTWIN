"""
AeroTwin — Phase 2A Reusable UI Components
===========================================
All HTML panel fragments and Plotly chart builders used by app.py.

Rules:
  - No <style> blocks here. All CSS is in styles.GLOBAL_CSS.
  - No st.* calls here — components return html strings or Plotly figures.
"""

from __future__ import annotations

import copy
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from styles import (
    COLORS, STATE_COLORS, STATE_BG_COLORS, STATE_ICONS,
    SENSOR_STATUS_COLORS, TREND_ICONS, CONSISTENCY_COLORS,
    SENSOR_CONFIG, SENSOR_ORDER, CHART_LAYOUT,
)


# ===========================================================================
# Section header helper
# ===========================================================================

def section_header(title: str, subtitle: str = "") -> str:
    sub_html = f'<div class="sec-subtitle">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="section-header">
        <div class="sec-label">{title}</div>
        {sub_html}
    </div>
    """


# ===========================================================================
# Top header bar
# ===========================================================================

def render_topbar_html() -> str:
    return """
    <div class="topbar">
        <div class="topbar-left">
            <div class="topbar-brand">⬡ AEROTWIN</div>
            <div class="topbar-subtitle">AI-Powered UAV Engine Health Monitor</div>
        </div>
        <div class="topbar-right">
            <div class="status-pill">
                <div class="status-dot"></div>
                SYSTEM ONLINE
            </div>
            <div class="demo-badge">⬡ DEMO MODE</div>
            <div class="topbar-team">AeroSentinels</div>
        </div>
    </div>
    """


# ===========================================================================
# Engine Health Hero Panel
# ===========================================================================

def render_health_hero_html(data: dict) -> str:
    state  = data["health_state"]
    score  = data["anomaly_score"]
    conf   = data["confidence"]
    color  = STATE_COLORS.get(state, COLORS["accent"])
    bg     = STATE_BG_COLORS.get(state, COLORS["bg_card"])
    icon   = STATE_ICONS.get(state, "●")

    def gauge_width(val: float) -> int:
        return max(2, min(100, int(val * 100)))

    score_pct = gauge_width(score)
    conf_pct  = gauge_width(conf / 100)

    if score < 0.35:
        score_color = COLORS["normal"]
    elif score < 0.65:
        score_color = COLORS["warning"]
    elif score < 0.85:
        score_color = COLORS["alarm"]
    else:
        score_color = COLORS["emergency"]

    return f"""
    <div class="hero-panel" style="border-left:3px solid {color};">
        <div class="hero-hex" style="color:{color}20;">⬡</div>
        <div>
            <div class="hero-label">// ENGINE HEALTH STATUS</div>
            <div class="hero-state"
                 style="background:{bg}; border:1px solid {color}; color:{color}; box-shadow:0 0 16px {color}30;">
                {icon}&nbsp;{state}
            </div>
            <div class="hero-metrics">
                <div class="hero-metric">
                    <div class="hm-label">Anomaly Score</div>
                    <div class="hm-value" style="color:{score_color};">{score:.2f}</div>
                    <div class="gauge-bar">
                        <div class="gauge-fill" style="width:{score_pct}%; background:{score_color};"></div>
                    </div>
                </div>
                <div class="hero-metric">
                    <div class="hm-label">AI Confidence</div>
                    <div class="hm-value" style="color:{COLORS["accent"]};">{conf:.0f}%</div>
                    <div class="gauge-bar">
                        <div class="gauge-fill" style="width:{conf_pct}%; background:{COLORS["accent"]};"></div>
                    </div>
                </div>
            </div>
            <div class="conf-note">
                ⚠ Prototype confidence indicator — not a calibrated probability.
                All values are DEMO/MOCK data.
            </div>
        </div>
    </div>
    """


# ===========================================================================
# Diagnosis Panel
# ===========================================================================

def render_diagnosis_html(data: dict) -> str:
    diag  = data["diagnosis"]
    state = data["health_state"]
    color = STATE_COLORS.get(state, COLORS["accent"])
    expl  = data["explanation"]

    diagnosis_icons = {
        "No Anomaly":                "✓",
        "Possible Sensor Issue":     "⚠",
        "Likely Engine Degradation": "⬡",
        "Insufficient Evidence":     "?",
    }
    d_icon = diagnosis_icons.get(diag, "⬡")

    return f"""
    <div class="diag-panel"
         style="background:{COLORS["bg_panel"]}; border-left:3px solid {color};">
        <div class="diag-header">// ENGINE DIAGNOSIS</div>
        <div class="diag-value" style="color:{color};">{d_icon}&nbsp;{diag}</div>
        <div class="diag-expl">{expl[:280]}</div>
    </div>
    """


# ===========================================================================
# Sensor Cards
# ===========================================================================

def render_sensor_card_html(sensor_key: str, data: dict) -> str:
    cfg    = SENSOR_CONFIG[sensor_key]
    val    = data["sensor_values"].get(sensor_key, 0)
    trend  = data["sensor_trends"].get(sensor_key, "STABLE")
    status = data["sensor_statuses"].get(sensor_key, "NORMAL")
    color  = SENSOR_STATUS_COLORS.get(status, COLORS["normal"])
    t_icon = TREND_ICONS.get(trend, "→")
    formatted_val = cfg["format"].format(val)

    return f"""
    <div class="sensor-card" style="border-top:2px solid {cfg["color"]};">
        <div class="sc-icon-label">
            <span class="sc-icon">{cfg["icon"]}</span>
            <span class="sc-label">{cfg["label"]}</span>
        </div>
        <div class="sc-value">
            {formatted_val}<span class="sc-unit">{cfg["unit"]}</span>
        </div>
        <div class="sc-trend">{t_icon} {trend}</div>
        <div class="sc-status"
             style="color:{color}; background:{color}15; border:1px solid {color}40;">
            {status}
        </div>
    </div>
    """


# ===========================================================================
# Explainable AI — bar contribution chart
# ===========================================================================

def render_xai_html(data: dict) -> str:
    contribs = data["sensor_contributions"]
    expl     = data["explanation"]

    sorted_contribs = sorted(contribs.items(), key=lambda x: x[1], reverse=True)

    bars_html = ""
    for sensor_key, weight in sorted_contribs:
        cfg      = SENSOR_CONFIG.get(sensor_key, {})
        label    = cfg.get("label", sensor_key.upper())
        bar_col  = cfg.get("color", COLORS["accent"])
        pct      = int(weight * 100)
        bars_html += (
            f'<div style="display:flex; align-items:center; gap:0.8rem; margin-bottom:0.55rem;">'
            f'<div style="font-family:\'JetBrains Mono\',monospace; font-size:0.68rem;'
            f' color:{COLORS["text_secondary"]}; width:110px; text-align:right;'
            f' flex-shrink:0; letter-spacing:0.04em;">{label}</div>'
            f'<div style="flex:1; height:10px; background:{COLORS["bg_base"]}; border-radius:2px;'
            f' overflow:hidden; border:1px solid {COLORS["border"]};">'
            f'<div style="width:{pct}%; height:100%;'
            f' background:linear-gradient(90deg, {bar_col}cc, {bar_col});'
            f' border-radius:2px; transition:width 0.4s ease;"></div>'
            f'</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace; font-size:0.63rem;'
            f' color:{bar_col}; width:32px; flex-shrink:0;">{pct}%</div>'
            f'</div>'
        )

    return f"""
    <div class="xai-panel">
        <div class="xai-header">// WHY IS THE ENGINE FLAGGED?</div>
        <div class="xai-subheader">Sensor contribution to anomaly score (relative, demo values)</div>
        {bars_html}
        <div class="xai-expl">{expl}</div>
    </div>
    """


# ===========================================================================
# Signal Consistency Panel
# ===========================================================================

def render_consistency_html(data: dict) -> str:
    consistency = data["signal_consistency"]
    diag_conf   = data["diagnosis_confidence"]
    note        = data["consistency_note"]
    diagnosis   = data["diagnosis"]
    c_color     = CONSISTENCY_COLORS.get(consistency, COLORS["accent"])
    d_color     = CONSISTENCY_COLORS.get(diag_conf, COLORS["accent"])

    return f"""
    <div class="consist-panel">
        <div class="consist-header">// ENGINE SIGNAL CONSISTENCY</div>
        <div class="consist-diag">{diagnosis}</div>
        <div class="consist-row">
            <div class="consist-item">
                <div class="ci-label">Sensor Agreement</div>
                <div class="ci-value" style="color:{c_color};">{consistency}</div>
            </div>
            <div class="consist-item">
                <div class="ci-label">Diagnosis Confidence</div>
                <div class="ci-value" style="color:{d_color};">{diag_conf}</div>
            </div>
        </div>
        <div class="consist-note">{note}</div>
    </div>
    """


# ===========================================================================
# Operator Interpretation Panel
# ===========================================================================

def render_interpretation_html(data: dict) -> str:
    interp = data["interpretation"]
    recom  = data["recommendation"]
    state  = data["health_state"]
    color  = STATE_COLORS.get(state, COLORS["accent"])

    return f"""
    <div class="interp-panel"
         style="background:{COLORS["bg_panel"]}; border-left:3px solid {color};">
        <div class="interp-header">// CURRENT INTERPRETATION</div>
        <div class="interp-text">{interp}</div>
        <div class="recom-label">Suggested Action</div>
        <div class="recom-text" style="color:{color};">{recom}</div>
    </div>
    """


# ===========================================================================
# Footer
# ===========================================================================

def render_footer_html() -> str:
    return """
    <div class="footer">
        <div class="footer-brand">⬡ AEROTWIN &bull; AEROSENTINELS</div>
        <div class="footer-notice">
            Software prototype using synthetic piston-engine-style telemetry.<br>
            Not certified for real-world flight or safety-critical decisions.
        </div>
    </div>
    """


# ===========================================================================
# Plotly — Sensor Trend Chart
# ===========================================================================

def build_sensor_trend_figure(data: dict, selected_sensors: list) -> go.Figure:
    ts      = data["timestamps"]
    trend_d = data["trend_data"]

    layout = copy.deepcopy(CHART_LAYOUT)
    layout["title"] = dict(
        text="ENGINE BEHAVIOUR TIMELINE",
        font=dict(family="'JetBrains Mono', monospace", color=COLORS["text_secondary"], size=12),
        x=0, xref="paper",
    )
    layout["xaxis"]["title"] = dict(text="TIME", font=dict(size=10, color=COLORS["text_muted"]))
    layout["height"] = 320

    if not selected_sensors:
        return go.Figure(layout=layout)

    fig = make_subplots(specs=[[{"secondary_y": False}]])

    # Build per-sensor y-axis IDs
    y_axes: dict[str, str] = {}
    for idx, sensor_key in enumerate(selected_sensors):
        y_axes[sensor_key] = "y" if idx == 0 else f"y{idx + 1}"

    for idx, sensor_key in enumerate(selected_sensors):
        if sensor_key not in trend_d:
            continue
        cfg   = SENSOR_CONFIG.get(sensor_key, {})
        label = cfg.get("label", sensor_key)
        color = cfg.get("color", COLORS["accent"])
        unit  = cfg.get("unit", "")
        y_id  = y_axes[sensor_key]

        # Plotly 5+ layout keys: "yaxis", "yaxis2", "yaxis3", …
        layout_key = "yaxis" if idx == 0 else f"yaxis{idx + 1}"

        layout[layout_key] = dict(
            title=dict(text=f"{label} ({unit})", font=dict(size=9, color=color)),
            tickfont=dict(color=color, size=9),
            gridcolor=COLORS["border"],
            linecolor=COLORS["border"],
            showgrid=(idx == 0),
            zeroline=False,
            overlaying="y" if idx > 0 else None,
            side="left" if idx % 2 == 0 else "right",
            position=0 if idx == 0 else min(1, idx * 0.10),
            showline=True,
            fixedrange=False,
        )

        fig.add_trace(go.Scatter(
            x=ts,
            y=trend_d[sensor_key],
            name=label,
            line=dict(color=color, width=1.5),
            mode="lines",
            hovertemplate=f"<b>{label}</b><br>%{{x}}<br>%{{y:.2f}} {unit}<extra></extra>",
            yaxis=y_id,
        ))

    layout["xaxis"]["showgrid"] = True
    fig.update_layout(**layout)
    return fig


# ===========================================================================
# Plotly — Anomaly Score Chart
# ===========================================================================

def build_anomaly_figure(data: dict) -> go.Figure:
    ts         = data["timestamps"]
    anom_trend = data["anomaly_trend"]
    layout = copy.deepcopy(CHART_LAYOUT)
    layout["title"] = dict(
        text="ANOMALY SCORE OVER TIME",
        font=dict(family="'JetBrains Mono', monospace", color=COLORS["text_secondary"], size=12),
        x=0, xref="paper",
    )
    layout["height"] = 200
    layout["yaxis"]["range"] = [0, 1.05]
    layout["yaxis"]["title"] = dict(text="SCORE", font=dict(size=10, color=COLORS["text_muted"]))

    fig = go.Figure(layout=layout)

    fig.add_trace(go.Scatter(
        x=ts, y=anom_trend,
        fill="tozeroy",
        fillcolor="rgba(255,179,0,0.08)",
        line=dict(color=COLORS["chart_anom"], width=1.5),
        mode="lines",
        name="Anomaly Score",
        hovertemplate="<b>Anomaly Score</b><br>%{x}<br>%{y:.3f}<extra></extra>",
    ))

    for thresh, label, col in [
        (0.35, "WARNING",   COLORS["warning"]),
        (0.65, "ALARM",     COLORS["alarm"]),
        (0.85, "EMERGENCY", COLORS["emergency"]),
    ]:
        fig.add_hline(
            y=thresh,
            line=dict(color=col, width=1, dash="dot"),
            annotation_text=label,
            annotation_font=dict(size=9, color=col, family="'JetBrains Mono', monospace"),
            annotation_position="right",
        )

    return fig


# ===========================================================================
# Plotly — Health State Timeline
# ===========================================================================

def build_health_timeline_figure(data: dict) -> go.Figure:
    ts     = data["timestamps"]
    ht     = data["health_timeline"]
    layout = copy.deepcopy(CHART_LAYOUT)
    layout["title"] = dict(
        text="HEALTH STATE TIMELINE",
        font=dict(family="'JetBrains Mono', monospace", color=COLORS["text_secondary"], size=12),
        x=0, xref="paper",
    )
    layout["height"] = 160
    layout["yaxis"] = dict(
        tickvals=[0, 1, 2, 3],
        ticktext=["NORMAL", "WARNING", "ALARM", "EMERGENCY"],
        tickfont=dict(size=9, color=COLORS["text_secondary"], family="'JetBrains Mono', monospace"),
        gridcolor=COLORS["border"],
        range=[-0.5, 3.5],
        fixedrange=True,
    )
    layout["xaxis"]["showgrid"] = False

    state_num = {"NORMAL": 0, "WARNING": 1, "ALARM": 2, "EMERGENCY": 3}
    y_vals    = [state_num.get(s, 0) for s in ht]
    bar_cols  = [STATE_COLORS.get(s, COLORS["normal"]) for s in ht]

    fig = go.Figure(layout=layout)
    fig.add_trace(go.Bar(
        x=ts,
        y=[1] * len(ts),
        base=y_vals,
        marker=dict(color=bar_cols, line=dict(width=0)),
        hovertemplate="<b>%{customdata}</b><br>%{x}<extra></extra>",
        customdata=ht,
        name="Health State",
        showlegend=False,
    ))

    return fig
