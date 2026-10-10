import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AeroTwin | AeroSentinels",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Dark aerospace theme adjustments */
    .stApp {
        background-color: #0E1117;
        color: #E0E6ED;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4DA8DA;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem;
        font-weight: 300;
        color: #A0B2C6;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    .team-branding {
        font-size: 0.9rem;
        color: #7A8B9C;
        font-style: italic;
    }
    .metric-card {
        background-color: #1A202C;
        border: 1px solid #2D3748;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .status-healthy { color: #38A169; font-weight: bold; }
    .status-warning { color: #D69E2E; font-weight: bold; }
    .status-danger { color: #E53E3E; font-weight: bold; }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- MOCK DATA SCENARIOS (Phase 2A Demo) ---
SCENARIOS = {
    "Healthy": {
        "engine_status": ("HEALTHY", "normal", "#38A169"),
        "anomaly_score": 0.05,
        "ai_confidence": 98.2,
        "diagnosis": "No Anomaly Detected. All systems operating within normal parameters.",
        "sensors": {
            "RPM": {"value": 5200, "trend": "steady", "status": "normal"},
            "Oil Pressure": {"value": 45.2, "trend": "steady", "status": "normal"},
            "Oil Temperature": {"value": 180.5, "trend": "steady", "status": "normal"},
            "EGT": {"value": 1250.0, "trend": "steady", "status": "normal"},
            "Vibration": {"value": 1.2, "trend": "steady", "status": "normal"},
        },
        "contributions": {"RPM": 0.1, "Oil Pressure": 0.2, "Oil Temperature": 0.15, "EGT": 0.25, "Vibration": 0.3}
    },
    "Oil Pressure Degradation": {
        "engine_status": ("WARNING", "inverse", "#D69E2E"),
        "anomaly_score": 0.65,
        "ai_confidence": 89.5,
        "diagnosis": "Possible Sensor Issue or early-stage fluid loss. Oil pressure dropping below optimal threshold.",
        "sensors": {
            "RPM": {"value": 5180, "trend": "steady", "status": "normal"},
            "Oil Pressure": {"value": 32.1, "trend": "down", "status": "warning"},
            "Oil Temperature": {"value": 185.0, "trend": "up", "status": "normal"},
            "EGT": {"value": 1260.0, "trend": "steady", "status": "normal"},
            "Vibration": {"value": 1.3, "trend": "up", "status": "normal"},
        },
        "contributions": {"RPM": 0.05, "Oil Pressure": 0.65, "Oil Temperature": 0.15, "EGT": 0.05, "Vibration": 0.1}
    },
    "EGT Increase": {
        "engine_status": ("WARNING", "inverse", "#D69E2E"),
        "anomaly_score": 0.72,
        "ai_confidence": 92.1,
        "diagnosis": "Likely Engine Degradation. EGT running excessively hot, possible mixture issue.",
        "sensors": {
            "RPM": {"value": 5150, "trend": "down", "status": "normal"},
            "Oil Pressure": {"value": 44.5, "trend": "steady", "status": "normal"},
            "Oil Temperature": {"value": 195.5, "trend": "up", "status": "warning"},
            "EGT": {"value": 1420.0, "trend": "up", "status": "danger"},
            "Vibration": {"value": 1.5, "trend": "up", "status": "normal"},
        },
        "contributions": {"RPM": 0.1, "Oil Pressure": 0.05, "Oil Temperature": 0.2, "EGT": 0.55, "Vibration": 0.1}
    },
    "Vibration Increase": {
        "engine_status": ("CRITICAL", "inverse", "#E53E3E"),
        "anomaly_score": 0.88,
        "ai_confidence": 96.4,
        "diagnosis": "Likely Engine Degradation. Severe mechanical vibration detected. Land as soon as possible.",
        "sensors": {
            "RPM": {"value": 5000, "trend": "down", "status": "warning"},
            "Oil Pressure": {"value": 43.0, "trend": "steady", "status": "normal"},
            "Oil Temperature": {"value": 182.0, "trend": "steady", "status": "normal"},
            "EGT": {"value": 1280.0, "trend": "up", "status": "normal"},
            "Vibration": {"value": 4.5, "trend": "up", "status": "danger"},
        },
        "contributions": {"RPM": 0.2, "Oil Pressure": 0.05, "Oil Temperature": 0.05, "EGT": 0.1, "Vibration": 0.6}
    },
    "Multi-Sensor Degradation": {
        "engine_status": ("CRITICAL", "inverse", "#E53E3E"),
        "anomaly_score": 0.95,
        "ai_confidence": 99.1,
        "diagnosis": "Likely Engine Degradation. Cascading failure signatures across thermal and mechanical systems.",
        "sensors": {
            "RPM": {"value": 4800, "trend": "down", "status": "danger"},
            "Oil Pressure": {"value": 28.5, "trend": "down", "status": "danger"},
            "Oil Temperature": {"value": 210.0, "trend": "up", "status": "danger"},
            "EGT": {"value": 1380.0, "trend": "up", "status": "danger"},
            "Vibration": {"value": 3.8, "trend": "up", "status": "danger"},
        },
        "contributions": {"RPM": 0.2, "Oil Pressure": 0.25, "Oil Temperature": 0.2, "EGT": 0.15, "Vibration": 0.2}
    },
    "Sensor-Only Abnormality": {
        "engine_status": ("INVESTIGATE", "off", "#805AD5"),
        "anomaly_score": 0.45,
        "ai_confidence": 65.0,
        "diagnosis": "Possible Sensor Issue / Insufficient Evidence. Erratic reading on Oil Pressure, but other parameters nominal.",
        "sensors": {
            "RPM": {"value": 5200, "trend": "steady", "status": "normal"},
            "Oil Pressure": {"value": 0.0, "trend": "down", "status": "danger"},
            "Oil Temperature": {"value": 180.5, "trend": "steady", "status": "normal"},
            "EGT": {"value": 1250.0, "trend": "steady", "status": "normal"},
            "Vibration": {"value": 1.2, "trend": "steady", "status": "normal"},
        },
        "contributions": {"RPM": 0.05, "Oil Pressure": 0.8, "Oil Temperature": 0.05, "EGT": 0.05, "Vibration": 0.05}
    }
}

# --- HELPER FUNCTIONS ---
def generate_timeseries(base_val, trend_type, volatility, points=50):
    np.random.seed(42) # For consistent mock data during demo
    time_index = pd.date_range(start=datetime.now() - timedelta(minutes=points), periods=points, freq='1T')
    
    if trend_type == "up":
        trend = np.linspace(0, base_val * 0.2, points)
    elif trend_type == "down":
        trend = np.linspace(0, -base_val * 0.2, points)
    else:
        trend = np.zeros(points)
        
    noise = np.random.normal(0, base_val * volatility, points)
    values = base_val + trend + noise
    
    return pd.DataFrame({"Time": time_index, "Value": values})

# --- SIDEBAR: SCENARIO SELECTOR (Phase 2A) ---
with st.sidebar:
    st.markdown("<div class='team-branding'>Team: AeroSentinels</div>", unsafe_allow_html=True)
    st.title("Demo Controls")
    
    st.info("⚠️ **Phase 2A MOCK DATA**\\n\\nThe values shown are for UI demonstration only. They are not connected to real engine sensors or the Phase 1 ML pipeline.")
    
    selected_scenario = st.selectbox(
        "Select Scenario:",
        list(SCENARIOS.keys())
    )
    
    current_data = SCENARIOS[selected_scenario]

# --- MAIN CONTENT ---

# 1. HEADER
st.markdown("<div class='main-header'>AeroTwin</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>AI-Powered UAV Engine Health Monitor</div>", unsafe_allow_html=True)

st.divider()

# 2. TOP STATUS SECTION
st.markdown("### System Overview")
col1, col2, col3 = st.columns(3)

with col1:
    status_text, status_delta, status_color = current_data["engine_status"]
    st.metric(label="ENGINE STATUS", value=status_text)
    # Using a simple markdown box to colorize status prominently
    st.markdown(f"<div style='background-color:{status_color}20; border-left: 5px solid {status_color}; padding: 10px; border-radius: 4px; color: {status_color}; font-weight: bold;'>Current Status: {status_text}</div>", unsafe_allow_html=True)

with col2:
    st.metric(label="ANOMALY SCORE", value=f"{current_data['anomaly_score']:.2f}", delta="Risk Level", delta_color=status_delta)
    st.progress(current_data['anomaly_score'])

with col3:
    st.metric(label="AI CONFIDENCE", value=f"{current_data['ai_confidence']}%")
    st.progress(current_data['ai_confidence']/100)

st.divider()

# 4. DIAGNOSIS SECTION
st.markdown("### AI Diagnosis")
st.info(f"**{current_data['diagnosis']}**")

st.divider()

# 3. FIVE SENSOR CARDS
st.markdown("### Real-Time Sensor Telemetry")
s_cols = st.columns(5)
sensors = current_data["sensors"]

sensor_units = {
    "RPM": "rev/min",
    "Oil Pressure": "PSI",
    "Oil Temperature": "°F",
    "EGT": "°F",
    "Vibration": "g"
}

for i, (sensor_name, s_data) in enumerate(sensors.items()):
    with s_cols[i]:
        # Determine delta for visual indication
        delta_val = ""
        if s_data["trend"] == "up": delta_val = "↗ Increasing"
        elif s_data["trend"] == "down": delta_val = "↘ Decreasing"
        else: delta_val = "→ Steady"
        
        # Invert colors for RPM/Pressure drops being bad, Temp/Vib increases being bad
        if sensor_name in ["RPM", "Oil Pressure"]:
            delta_color = "normal" if s_data["trend"] != "down" else "inverse"
        else:
            delta_color = "inverse" if s_data["trend"] != "down" else "normal"
            
        if s_data["trend"] == "steady": delta_color = "off"
        
        st.metric(
            label=sensor_name,
            value=f"{s_data['value']} {sensor_units[sensor_name]}",
            delta=delta_val,
            delta_color=delta_color
        )
        status = s_data['status']
        color_map = {"normal": "#38A169", "warning": "#D69E2E", "danger": "#E53E3E"}
        st.markdown(f"<div style='color: {color_map[status]}; font-size: 0.8rem; font-weight: bold;'>STATUS: {status.upper()}</div>", unsafe_allow_html=True)

st.divider()

# 5. EXPLAINABLE AI SECTION & 6. TREND GRAPH SECTION
st.markdown("### Diagnostics & Trends")

tab1, tab2 = st.tabs(["Explainable AI (Why Flagged?)", "Sensor Trends"])

with tab1:
    st.markdown("#### Feature Contributions to Anomaly Score")
    st.write("This chart shows which sensors are driving the current anomaly prediction.")
    
    # Simple Bar chart for contributions
    contribs = current_data["contributions"]
    df_contrib = pd.DataFrame({
        "Sensor": list(contribs.keys()),
        "Contribution": list(contribs.values())
    }).sort_values("Contribution", ascending=True)
    
    fig_contrib = px.bar(
        df_contrib, 
        x="Contribution", 
        y="Sensor", 
        orientation='h',
        color="Contribution",
        color_continuous_scale="Reds"
    )
    fig_contrib.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E0E6ED"),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_contrib, use_container_width=True)

with tab2:
    st.markdown("#### Historical Telemetry (Mock Data)")
    
    selected_sensor_trend = st.selectbox("Select Sensor to View Trend:", list(sensors.keys()))
    
    # Generate mock timeseries data
    base_val = sensors[selected_sensor_trend]["value"]
    trend = sensors[selected_sensor_trend]["trend"]
    df_trend = generate_timeseries(base_val, trend, volatility=0.02)
    
    fig_trend = px.line(
        df_trend, 
        x="Time", 
        y="Value", 
        title=f"{selected_sensor_trend} - Last 50 Minutes"
    )
    
    fig_trend.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E0E6ED"),
        xaxis_title="",
        yaxis_title=sensor_units[selected_sensor_trend]
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7A8B9C; font-size: 0.8rem;'>"
    "AeroTwin Phase 2A Dashboard Prototype | Developed by AeroSentinels<br>"
    "Note: This is a UI skeleton using demonstration data. "
    "Not for actual flight operations or real-time diagnostic use."
    "</div>", 
    unsafe_allow_html=True
)
