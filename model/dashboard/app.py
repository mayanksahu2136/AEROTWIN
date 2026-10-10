"""
AeroTwin — Phase 2A Main Dashboard
=====================================
Entry point: streamlit run dashboard/app.py

PHASE 2B NOTE:
    To connect real Phase 1 outputs, replace the import and call to
    demo_data.get_scenario_data() with the Phase 1 pipeline runner.
    The DashboardData dict structure is documented in demo_data.py.
"""

from __future__ import annotations

import sys
import os

# Make sure dashboard/ is on path when run from project root
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── Internal modules ─────────────────────────────────────────────────────────
from styles import GLOBAL_CSS, COLORS, SENSOR_ORDER
from demo_data import get_scenario_data, get_all_scenario_names
from components import (
    render_topbar_html,
    render_health_hero_html,
    render_diagnosis_html,
    render_sensor_card_html,
    render_xai_html,
    render_consistency_html,
    render_interpretation_html,
    render_footer_html,
    build_sensor_trend_figure,
    build_anomaly_figure,
    build_health_timeline_figure,
    section_header,
)

# ===========================================================================
# Page config — must be first Streamlit call
# ===========================================================================

st.set_page_config(
    page_title="AeroTwin | UAV Engine Health Monitor",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===========================================================================
# Inject global CSS
# ===========================================================================

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ===========================================================================
# Sidebar — Scenario Control Panel
# ===========================================================================

with st.sidebar:
    st.markdown(f"""
    <div style="
        font-family:'JetBrains Mono',monospace;
        font-size:0.65rem;
        color:{COLORS["accent"]};
        letter-spacing:0.14em;
        text-transform:uppercase;
        margin-bottom:0.2rem;
        padding-bottom:0.5rem;
        border-bottom:1px solid {COLORS["border"]};
    ">⬡ SCENARIO CONTROL</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        font-family:'Space Grotesk',sans-serif;
        font-size:0.72rem;
        color:{COLORS["text_muted"]};
        margin-bottom:1rem;
        line-height:1.5;
    ">
        Select a demo scenario to update all dashboard panels.
        These are DEMO values only — Phase 1 pipeline not connected.
    </div>
    """, unsafe_allow_html=True)

    scenario_names = get_all_scenario_names()
    selected_scenario = st.radio(
        "DEMO SCENARIO",
        scenario_names,
        index=1,
        key="scenario_selector",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Sensor selector for trend chart
    st.markdown(f"""
    <div style="
        font-family:'JetBrains Mono',monospace;
        font-size:0.62rem;
        color:{COLORS["accent"]};
        letter-spacing:0.12em;
        text-transform:uppercase;
        margin-bottom:0.3rem;
    ">TREND CHART SENSORS</div>
    """, unsafe_allow_html=True)

    sensor_labels = {
        "RPM":             "RPM",
        "oil_pressure":    "Oil Pressure",
        "oil_temperature": "Oil Temperature",
        "EGT":             "EGT",
        "vibration":       "Vibration",
    }
    selected_sensors = st.multiselect(
        "Display sensors",
        options=list(sensor_labels.keys()),
        default=["RPM", "oil_pressure", "vibration"],
        format_func=lambda k: sensor_labels[k],
        key="sensor_selector",
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        font-family:'Space Grotesk',sans-serif;
        font-size:0.65rem;
        color:{COLORS["text_muted"]};
        line-height:1.6;
    ">
        <b style="color:{COLORS["text_secondary"]};">Phase 2A — Demo Mode</b><br>
        All values are synthetic mock data.<br>
        Phase 2B will connect to Phase 1 ML pipeline.<br><br>
        <span style="color:{COLORS["text_muted"]};">Run: <code style="color:{COLORS["accent"]};">streamlit run dashboard/app.py</code></span>
    </div>
    """, unsafe_allow_html=True)

# ===========================================================================
# Load data for selected scenario
# ===========================================================================

data = get_scenario_data(selected_scenario)

# ===========================================================================
# SECTION 1 — Top Header
# ===========================================================================

st.markdown(render_topbar_html(), unsafe_allow_html=True)

# ===========================================================================
# SECTION 2+3 — Hero Panel + Diagnosis (side by side)
# ===========================================================================

col_hero, col_diag = st.columns([3, 2], gap="small")

with col_hero:
    st.markdown(render_health_hero_html(data), unsafe_allow_html=True)

with col_diag:
    st.markdown(render_diagnosis_html(data), unsafe_allow_html=True)
    st.markdown(render_interpretation_html(data), unsafe_allow_html=True)

# ===========================================================================
# SECTION 4 — Sensor Cards
# ===========================================================================

st.markdown(section_header("SENSOR MONITORING", "Five-parameter engine telemetry"), unsafe_allow_html=True)

sensor_cols = st.columns(5, gap="small")
for i, sensor_key in enumerate(SENSOR_ORDER):
    with sensor_cols[i]:
        st.markdown(render_sensor_card_html(sensor_key, data), unsafe_allow_html=True)

# ===========================================================================
# SECTION 5+6 — XAI + Signal Consistency
# ===========================================================================

st.markdown(section_header("ANOMALY ANALYSIS"), unsafe_allow_html=True)

col_xai, col_consist = st.columns([3, 2], gap="small")

with col_xai:
    st.markdown(render_xai_html(data), unsafe_allow_html=True)

with col_consist:
    st.markdown(render_consistency_html(data), unsafe_allow_html=True)

# ===========================================================================
# SECTION 7 — Trend Analysis
# ===========================================================================

st.markdown(section_header("TREND ANALYSIS", "Engine behaviour over the last 10 minutes (demo data)"), unsafe_allow_html=True)

# Sensor trend chart
trend_fig = build_sensor_trend_figure(data, selected_sensors)
st.plotly_chart(
    trend_fig,
    width="stretch",
    config=dict(
        displayModeBar=True,
        displaylogo=False,
        modeBarButtonsToRemove=["select2d", "lasso2d", "autoScale2d"],
        toImageButtonOptions=dict(format="png", filename="aerotwin_sensor_trend"),
    ),
    key="sensor_trend_chart",
)

# Anomaly score + health timeline side by side
col_anom, col_htl = st.columns([3, 2], gap="small")

with col_anom:
    anom_fig = build_anomaly_figure(data)
    st.plotly_chart(
        anom_fig,
        width="stretch",
        config=dict(displayModeBar=False, displaylogo=False),
        key="anomaly_chart",
    )

with col_htl:
    htl_fig = build_health_timeline_figure(data)
    st.plotly_chart(
        htl_fig,
        width="stretch",
        config=dict(displayModeBar=False, displaylogo=False),
        key="health_timeline_chart",
    )

# ===========================================================================
# SECTION 10 — Footer
# ===========================================================================

st.markdown(render_footer_html(), unsafe_allow_html=True)
