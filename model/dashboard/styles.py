"""
AeroTwin — Phase 2A Styles & Theme
====================================
Central place for all colour tokens, status mappings, and chart themes.

Phase 2B does not need to change this file.

IMPORTANT: All component CSS classes are defined in GLOBAL_CSS below.
Component render functions must NOT include <style> blocks — they
return plain HTML using the class names defined here.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Colour palette — aerospace dark theme
# ---------------------------------------------------------------------------

COLORS = {
    # Background hierarchy
    "bg_base":       "#08090d",
    "bg_surface":    "#0d0f18",
    "bg_panel":      "#11141f",
    "bg_card":       "#161925",
    "bg_card_hover": "#1c2030",

    # Accent
    "accent":        "#00c8ff",
    "accent_dim":    "#0087aa",
    "accent_glow":   "rgba(0,200,255,0.15)",

    # Status colours
    "normal":        "#00e676",
    "normal_dim":    "#004d25",
    "warning":       "#ffb300",
    "warning_dim":   "#4d3600",
    "alarm":         "#ff5722",
    "alarm_dim":     "#4d1a0a",
    "emergency":     "#ff1744",
    "emergency_dim": "#4d0013",

    # Secondary status
    "caution":       "#ffd740",
    "caution_dim":   "#4d4000",

    # Text
    "text_primary":  "#e8ecf4",
    "text_secondary":"#8a95a8",
    "text_muted":    "#4a5568",
    "text_label":    "#6b7a90",

    # Grid/border
    "border":        "#1e2535",
    "border_accent": "#2a3550",

    # Chart palette (sensor lines)
    "chart_rpm":     "#00c8ff",
    "chart_oilp":    "#ff9500",
    "chart_oilt":    "#ff5722",
    "chart_egt":     "#ff1744",
    "chart_vib":     "#aa00ff",
    "chart_anom":    "#ffb300",
}

# ---------------------------------------------------------------------------
# Status colour mapping
# ---------------------------------------------------------------------------

STATE_COLORS = {
    "NORMAL":    COLORS["normal"],
    "WARNING":   COLORS["warning"],
    "ALARM":     COLORS["alarm"],
    "EMERGENCY": COLORS["emergency"],
}

STATE_BG_COLORS = {
    "NORMAL":    COLORS["normal_dim"],
    "WARNING":   COLORS["warning_dim"],
    "ALARM":     COLORS["alarm_dim"],
    "EMERGENCY": COLORS["emergency_dim"],
}

STATE_ICONS = {
    "NORMAL":    "●",
    "WARNING":   "⚠",
    "ALARM":     "🔴",
    "EMERGENCY": "🚨",
}

SENSOR_STATUS_COLORS = {
    "NORMAL":  COLORS["normal"],
    "CAUTION": COLORS["caution"],
    "WARNING": COLORS["warning"],
    "ALARM":   COLORS["alarm"],
}

TREND_ICONS = {
    "STABLE":     "→",
    "INCREASING": "↑",
    "DECREASING": "↓",
    "ERRATIC":    "↯",
}

CONSISTENCY_COLORS = {
    "HIGH":   COLORS["normal"],
    "MEDIUM": COLORS["warning"],
    "LOW":    COLORS["alarm"],
}

# ---------------------------------------------------------------------------
# Sensor display config
# ---------------------------------------------------------------------------

SENSOR_CONFIG = {
    "RPM": {
        "label":  "RPM",
        "unit":   "rpm",
        "icon":   "⚙",
        "color":  COLORS["chart_rpm"],
        "format": "{:.0f}",
    },
    "oil_pressure": {
        "label":  "OIL PRESSURE",
        "unit":   "bar",
        "icon":   "🛢",
        "color":  COLORS["chart_oilp"],
        "format": "{:.1f}",
    },
    "oil_temperature": {
        "label":  "OIL TEMP",
        "unit":   "°C",
        "icon":   "🌡",
        "color":  COLORS["chart_oilt"],
        "format": "{:.1f}",
    },
    "EGT": {
        "label":  "EGT",
        "unit":   "°C",
        "icon":   "🔥",
        "color":  COLORS["chart_egt"],
        "format": "{:.0f}",
    },
    "vibration": {
        "label":  "VIBRATION",
        "unit":   "g",
        "icon":   "〰",
        "color":  COLORS["chart_vib"],
        "format": "{:.2f}",
    },
}

SENSOR_ORDER = ["RPM", "oil_pressure", "oil_temperature", "EGT", "vibration"]

# ---------------------------------------------------------------------------
# Plotly chart base layout (reusable)
# ---------------------------------------------------------------------------

CHART_LAYOUT = dict(
    paper_bgcolor=COLORS["bg_panel"],
    plot_bgcolor=COLORS["bg_card"],
    font=dict(family="'Courier New', monospace", color=COLORS["text_secondary"], size=11),
    margin=dict(l=60, r=20, t=40, b=40),
    xaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border_accent"],
        tickfont=dict(color=COLORS["text_muted"], size=10),
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border_accent"],
        tickfont=dict(color=COLORS["text_muted"], size=10),
        showgrid=True,
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=COLORS["border"],
        borderwidth=1,
        font=dict(color=COLORS["text_secondary"], size=10),
    ),
    hoverlabel=dict(
        bgcolor=COLORS["bg_card"],
        bordercolor=COLORS["accent"],
        font=dict(color=COLORS["text_primary"], size=11),
    ),
)

# ---------------------------------------------------------------------------
# Global Streamlit CSS injection
# ALL component class definitions live here.
# Component render functions must NOT emit <style> blocks.
# ---------------------------------------------------------------------------

_C = COLORS  # short alias for the f-string below

GLOBAL_CSS = (
    "<style>\n"
    "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700"
    "&family=JetBrains+Mono:wght@400;500;600&display=swap');\n\n"
    "*, *::before, *::after { box-sizing: border-box; }\n"
    f"html, body, [data-testid='stAppViewContainer'], [data-testid='stMain'], [data-testid='block-container'] {{ background-color: {_C['bg_base']} !important; color: {_C['text_primary']} !important; font-family: 'Space Grotesk', sans-serif !important; }}\n"
    "#MainMenu, footer, [data-testid='stToolbar'], header { display: none !important; }\n"
    f"[data-testid='stSidebar'] {{ background-color: {_C['bg_surface']} !important; border-right: 1px solid {_C['border']} !important; }}\n"
    f"[data-testid='stSidebar'] * {{ color: {_C['text_primary']} !important; }}\n"
    f".stSelectbox > div > div, .stMultiSelect > div > div {{ background-color: {_C['bg_card']} !important; border: 1px solid {_C['border_accent']} !important; color: {_C['text_primary']} !important; border-radius: 4px !important; }}\n"
    f".stSelectbox label, .stMultiSelect label, .stRadio label, .stCheckbox label {{ color: {_C['text_secondary']} !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.78rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }}\n"
    ".stRadio > div { gap: 0.5rem !important; }\n"
    f"[data-testid='stMetricValue'] {{ color: {_C['accent']} !important; font-family: 'JetBrains Mono', monospace !important; }}\n"
    f"hr {{ border-color: {_C['border']} !important; margin: 0.5rem 0 !important; }}\n"
    f"::-webkit-scrollbar {{ width: 6px; }} ::-webkit-scrollbar-track {{ background: {_C['bg_base']}; }} ::-webkit-scrollbar-thumb {{ background: {_C['border_accent']}; border-radius: 3px; }}\n"
    f".js-plotly-plot .plotly .modebar {{ background-color: {_C['bg_panel']} !important; }}\n"
    f".stButton > button {{ background-color: {_C['bg_card']} !important; border: 1px solid {_C['accent_dim']} !important; color: {_C['accent']} !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.75rem !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; transition: all 0.2s ease !important; }}\n"
    f".stButton > button:hover {{ border-color: {_C['accent']} !important; box-shadow: 0 0 8px {_C['accent_glow']} !important; }}\n"
    f".stTabs [data-baseweb='tab-list'] {{ background-color: {_C['bg_surface']} !important; border-bottom: 1px solid {_C['border']} !important; gap: 0 !important; }}\n"
    f".stTabs [data-baseweb='tab'] {{ background-color: transparent !important; color: {_C['text_secondary']} !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.72rem !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; border-bottom: 2px solid transparent !important; padding: 0.6rem 1.2rem !important; }}\n"
    f".stTabs [aria-selected='true'] {{ color: {_C['accent']} !important; border-bottom-color: {_C['accent']} !important; }}\n"
    f"[data-testid='stAlert'] {{ background-color: {_C['bg_card']} !important; border-left: 3px solid {_C['accent']} !important; }}\n\n"

    # --- TOPBAR ---
    f".topbar {{ display:flex; align-items:center; justify-content:space-between; padding:1rem 1.5rem 0.8rem 1.5rem; border-bottom:1px solid {_C['border']}; background:linear-gradient(180deg,{_C['bg_surface']} 0%,{_C['bg_base']} 100%); margin-bottom:0.5rem; }}\n"
    ".topbar-left { display:flex; flex-direction:column; gap:0.15rem; }\n"
    f".topbar-brand {{ font-family:'JetBrains Mono',monospace; font-size:1.6rem; font-weight:700; color:{_C['accent']}; letter-spacing:0.12em; text-shadow:0 0 20px rgba(0,200,255,0.4); }}\n"
    f".topbar-subtitle {{ font-family:'Space Grotesk',sans-serif; font-size:0.78rem; color:{_C['text_secondary']}; letter-spacing:0.06em; text-transform:uppercase; }}\n"
    ".topbar-right { display:flex; flex-direction:column; align-items:flex-end; gap:0.4rem; }\n"
    f".status-pill {{ display:inline-flex; align-items:center; gap:0.35rem; padding:0.25rem 0.75rem; border:1px solid {_C['normal_dim']}; border-radius:2px; background:rgba(0,230,118,0.07); font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:{_C['normal']}; letter-spacing:0.1em; }}\n"
    f".status-dot {{ width:7px; height:7px; border-radius:50%; background:{_C['normal']}; box-shadow:0 0 6px {_C['normal']}; animation:pulse-dot 2s ease-in-out infinite; }}\n"
    "@keyframes pulse-dot { 0%, 100% { opacity:1; } 50% { opacity:0.4; } }\n"
    f".demo-badge {{ font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:{_C['warning']}; background:rgba(255,179,0,0.10); border:1px solid rgba(255,179,0,0.25); border-radius:2px; padding:0.15rem 0.5rem; letter-spacing:0.1em; }}\n"
    f".topbar-team {{ font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:{_C['text_muted']}; letter-spacing:0.08em; text-transform:uppercase; }}\n\n"

    # --- SECTION HEADERS ---
    f".section-header {{ display:flex; align-items:baseline; gap:1rem; margin:1rem 0 0.5rem 0; padding-bottom:0.4rem; border-bottom:1px solid {_C['border']}; }}\n"
    f".sec-label {{ font-family:'JetBrains Mono',monospace; font-size:0.72rem; font-weight:600; color:{_C['accent']}; letter-spacing:0.14em; text-transform:uppercase; }}\n"
    f".sec-subtitle {{ font-family:'Space Grotesk',sans-serif; font-size:0.72rem; color:{_C['text_muted']}; }}\n\n"

    # --- HERO PANEL ---
    f".hero-panel {{ background:linear-gradient(135deg,{_C['bg_panel']} 0%,{_C['bg_card']} 100%); border:1px solid {_C['border_accent']}; border-radius:4px; padding:1.5rem 2rem; margin-bottom:0.5rem; position:relative; overflow:hidden; }}\n"
    f".hero-label {{ font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:{_C['text_muted']}; letter-spacing:0.16em; text-transform:uppercase; margin-bottom:0.4rem; }}\n"
    ".hero-state { display:inline-flex; align-items:center; gap:0.6rem; padding:0.4rem 1.2rem; border-radius:3px; font-family:'JetBrains Mono',monospace; font-size:1.5rem; font-weight:700; letter-spacing:0.16em; margin-bottom:1rem; }\n"
    ".hero-metrics { display:flex; gap:2.5rem; margin-top:0.5rem; }\n"
    ".hero-metric { display:flex; flex-direction:column; gap:0.3rem; }\n"
    f".hm-label {{ font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:{_C['text_muted']}; letter-spacing:0.12em; text-transform:uppercase; }}\n"
    ".hm-value { font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:600; line-height:1; }\n"
    f".gauge-bar {{ height:5px; background:{_C['bg_base']}; border-radius:3px; margin-top:0.3rem; width:140px; overflow:hidden; border:1px solid {_C['border']}; }}\n"
    ".gauge-fill { height:100%; border-radius:3px; transition:width 0.5s ease; }\n"
    f".conf-note {{ font-family:'Space Grotesk',sans-serif; font-size:0.62rem; color:{_C['text_muted']}; font-style:italic; margin-top:1rem; padding-top:0.8rem; border-top:1px solid {_C['border']}; }}\n"
    ".hero-hex { font-family:'JetBrains Mono',monospace; font-size:5rem; line-height:1; user-select:none; position:absolute; right:1.5rem; top:50%; transform:translateY(-50%); }\n\n"

    # --- DIAGNOSIS PANEL ---
    f".diag-panel {{ border:1px solid {_C['border']}; border-radius:4px; padding:1.2rem 1.5rem; margin-bottom:0.5rem; }}\n"
    f".diag-header {{ font-family:'JetBrains Mono',monospace; font-size:0.64rem; color:{_C['text_muted']}; letter-spacing:0.14em; text-transform:uppercase; margin-bottom:0.5rem; }}\n"
    ".diag-value { font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.7rem; }\n"
    f".diag-expl {{ font-family:'Space Grotesk',sans-serif; font-size:0.82rem; color:{_C['text_secondary']}; line-height:1.55; }}\n\n"

    # --- SENSOR CARDS ---
    f".sensor-card {{ background:{_C['bg_card']}; border:1px solid {_C['border']}; border-radius:4px; padding:1rem 1.1rem; transition:border-color 0.2s ease; height:100%; }}\n"
    ".sc-icon-label { display:flex; align-items:center; gap:0.4rem; margin-bottom:0.6rem; }\n"
    ".sc-icon { font-size:1rem; }\n"
    f".sc-label {{ font-family:'JetBrains Mono',monospace; font-size:0.63rem; color:{_C['text_muted']}; letter-spacing:0.12em; text-transform:uppercase; }}\n"
    f".sc-value {{ font-family:'JetBrains Mono',monospace; font-size:1.55rem; font-weight:600; color:{_C['text_primary']}; line-height:1.1; margin-bottom:0.1rem; }}\n"
    f".sc-unit {{ font-size:0.65rem; color:{_C['text_muted']}; margin-left:0.2rem; }}\n"
    f".sc-trend {{ font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:{_C['text_secondary']}; margin-bottom:0.5rem; }}\n"
    ".sc-status { display:inline-block; font-family:'JetBrains Mono',monospace; font-size:0.65rem; font-weight:600; border-radius:2px; padding:0.15rem 0.5rem; letter-spacing:0.1em; }\n\n"

    # --- XAI PANEL ---
    f".xai-panel {{ background:{_C['bg_panel']}; border:1px solid {_C['border']}; border-left:3px solid {_C['accent_dim']}; border-radius:4px; padding:1.2rem 1.5rem; }}\n"
    f".xai-header {{ font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:{_C['accent']}; letter-spacing:0.14em; text-transform:uppercase; margin-bottom:0.3rem; }}\n"
    f".xai-subheader {{ font-family:'Space Grotesk',sans-serif; font-size:0.72rem; color:{_C['text_muted']}; margin-bottom:1rem; }}\n"
    f".xai-expl {{ font-family:'Space Grotesk',sans-serif; font-size:0.82rem; color:{_C['text_secondary']}; line-height:1.6; margin-top:1rem; padding-top:0.8rem; border-top:1px solid {_C['border']}; }}\n\n"

    # --- SIGNAL CONSISTENCY PANEL ---
    f".consist-panel {{ background:{_C['bg_panel']}; border:1px solid {_C['border']}; border-radius:4px; padding:1.2rem 1.5rem; }}\n"
    f".consist-header {{ font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:{_C['accent']}; letter-spacing:0.14em; text-transform:uppercase; margin-bottom:0.8rem; }}\n"
    ".consist-row { display:flex; justify-content:space-between; margin-bottom:0.7rem; }\n"
    ".consist-item { display:flex; flex-direction:column; gap:0.25rem; }\n"
    f".ci-label {{ font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:{_C['text_muted']}; letter-spacing:0.10em; text-transform:uppercase; }}\n"
    ".ci-value { font-family:'JetBrains Mono',monospace; font-size:0.9rem; font-weight:600; letter-spacing:0.08em; }\n"
    f".consist-diag {{ font-family:'JetBrains Mono',monospace; font-size:0.8rem; font-weight:500; color:{_C['text_primary']}; margin-bottom:0.6rem; padding-bottom:0.5rem; border-bottom:1px solid {_C['border']}; }}\n"
    f".consist-note {{ font-family:'Space Grotesk',sans-serif; font-size:0.78rem; color:{_C['text_secondary']}; line-height:1.5; }}\n\n"

    # --- INTERPRETATION PANEL ---
    f".interp-panel {{ border:1px solid {_C['border']}; border-radius:4px; padding:1.1rem 1.5rem; }}\n"
    f".interp-header {{ font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:{_C['text_muted']}; letter-spacing:0.14em; text-transform:uppercase; margin-bottom:0.7rem; }}\n"
    f".interp-text {{ font-family:'Space Grotesk',sans-serif; font-size:0.85rem; color:{_C['text_primary']}; line-height:1.55; margin-bottom:0.7rem; }}\n"
    f".recom-label {{ font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:{_C['text_muted']}; letter-spacing:0.10em; text-transform:uppercase; margin-bottom:0.3rem; }}\n"
    ".recom-text { font-family:'Space Grotesk',sans-serif; font-size:0.82rem; line-height:1.5; }\n\n"

    # --- FOOTER ---
    f".footer {{ margin-top:2rem; padding:1rem 1.5rem; border-top:1px solid {_C['border']}; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; }}\n"
    f".footer-brand {{ font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:{_C['accent_dim']}; letter-spacing:0.1em; }}\n"
    f".footer-notice {{ font-family:'Space Grotesk',sans-serif; font-size:0.65rem; color:{_C['text_muted']}; text-align:right; line-height:1.5; }}\n"
    "</style>\n"
)
