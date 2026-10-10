"""
AeroTwin — Phase 2A Demo Data Module
=====================================
Provides mock/demo data for all six scenarios.

PHASE 2B NOTE:
    Replace get_scenario_data() with a call to Phase 1 pipeline output.
    The returned DashboardData dict structure is the canonical data interface.

    Required keys:
        sensor_values       : dict[str, float]
        anomaly_score       : float  (0.0 - 1.0)
        confidence          : float  (0 - 100)
        health_state        : str    (NORMAL | WARNING | ALARM | EMERGENCY)
        diagnosis           : str
        sensor_contributions: dict[str, float]  (0.0 - 1.0, relative weight)
        explanation         : str
        signal_consistency  : str   (HIGH | MEDIUM | LOW)
        diagnosis_confidence: str   (HIGH | MEDIUM | LOW)
        consistency_note    : str
        interpretation      : str
        recommendation      : str
        timestamps          : list[str]         (ISO-8601 strings)
        trend_data          : dict[str, list[float]]
        anomaly_trend       : list[float]
        health_timeline     : list[str]
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Type alias for the canonical data interface
# ---------------------------------------------------------------------------
DashboardData = Dict[str, Any]

# ---------------------------------------------------------------------------
# Scenario definitions
# ---------------------------------------------------------------------------
SCENARIOS = {
    "Healthy": 0,
    "Gradual Oil-Pressure Degradation": 1,
    "EGT Increase": 2,
    "Vibration Increase": 3,
    "Multi-Sensor Degradation": 4,
    "Sensor-Only Abnormality": 5,
}

SCENARIO_LIST = list(SCENARIOS.keys())

# ---------------------------------------------------------------------------
# Timeline generation helper
# ---------------------------------------------------------------------------
def _make_timestamps(n: int = 60) -> list:
    """Return a list of ISO-8601 timestamp strings ending at now."""
    now = datetime(2026, 10, 6, 14, 0, 0)
    step = timedelta(seconds=10)
    return [(now - step * (n - i - 1)).strftime("%Y-%m-%dT%H:%M:%S") for i in range(n)]


def _smooth_series(base: float, noise: float, n: int, drift: float = 0.0) -> list:
    """Generate a smooth noisy series with optional linear drift."""
    series = []
    val = base
    for i in range(n):
        val += drift + random.gauss(0, noise)
        series.append(round(val, 2))
    return series


# ---------------------------------------------------------------------------
# Per-scenario data builders
# ---------------------------------------------------------------------------

def _healthy() -> DashboardData:
    n = 60
    ts = _make_timestamps(n)
    rpm_series  = _smooth_series(2450, 12, n)
    oilp_series = _smooth_series(68.5, 0.4, n)
    oilt_series = _smooth_series(84.2, 0.6, n)
    egt_series  = _smooth_series(612, 4, n)
    vib_series  = _smooth_series(0.18, 0.008, n)
    anom_trend  = [round(random.uniform(0.05, 0.18), 3) for _ in range(n)]
    health_tl   = ["NORMAL"] * n

    return dict(
        sensor_values=dict(RPM=2451.0, oil_pressure=68.5, oil_temperature=84.2, EGT=613.0, vibration=0.18),
        sensor_trends=dict(RPM="STABLE", oil_pressure="STABLE", oil_temperature="STABLE", EGT="STABLE", vibration="STABLE"),
        sensor_statuses=dict(RPM="NORMAL", oil_pressure="NORMAL", oil_temperature="NORMAL", EGT="NORMAL", vibration="NORMAL"),
        anomaly_score=0.11,
        confidence=94.0,
        health_state="NORMAL",
        diagnosis="No Anomaly",
        sensor_contributions=dict(oil_pressure=0.15, vibration=0.12, EGT=0.10, RPM=0.08, oil_temperature=0.06),
        explanation="All sensor signals are within the learned healthy operating range. No deviations detected.",
        signal_consistency="HIGH",
        diagnosis_confidence="HIGH",
        consistency_note="All sensors are in agreement. Engine behaviour matches healthy baseline.",
        interpretation="Engine is operating normally. All parameters are within expected bounds.",
        recommendation="No action required. Continue normal operation.",
        timestamps=ts,
        trend_data=dict(RPM=rpm_series, oil_pressure=oilp_series, oil_temperature=oilt_series, EGT=egt_series, vibration=vib_series),
        anomaly_trend=anom_trend,
        health_timeline=health_tl,
    )


def _oil_pressure_degradation() -> DashboardData:
    n = 60
    ts = _make_timestamps(n)
    rpm_series  = _smooth_series(2430, 15, n)
    oilp_series = [round(68.5 - (i * 0.12) + random.gauss(0, 0.4), 2) for i in range(n)]
    oilt_series = _smooth_series(86.0, 1.0, n, drift=0.02)
    egt_series  = _smooth_series(618, 5, n)
    vib_series  = _smooth_series(0.22, 0.012, n, drift=0.0005)
    anom_trend  = [round(min(0.05 + i * 0.012 + random.uniform(0, 0.02), 0.95), 3) for i in range(n)]
    health_tl   = ["NORMAL"] * 25 + ["WARNING"] * 25 + ["ALARM"] * 10

    return dict(
        sensor_values=dict(RPM=2428.0, oil_pressure=62.4, oil_temperature=86.5, EGT=619.0, vibration=0.24),
        sensor_trends=dict(RPM="STABLE", oil_pressure="DECREASING", oil_temperature="INCREASING", EGT="STABLE", vibration="INCREASING"),
        sensor_statuses=dict(RPM="NORMAL", oil_pressure="WARNING", oil_temperature="CAUTION", EGT="NORMAL", vibration="CAUTION"),
        anomaly_score=0.72,
        confidence=87.0,
        health_state="WARNING",
        diagnosis="Likely Engine Degradation",
        sensor_contributions=dict(oil_pressure=0.88, vibration=0.62, EGT=0.35, RPM=0.18, oil_temperature=0.14),
        explanation=(
            "Oil pressure is steadily decreasing while vibration is gradually increasing. "
            "These are correlated deviations from the learned healthy pattern, "
            "suggesting an engine-related issue rather than a single sensor fault."
        ),
        signal_consistency="HIGH",
        diagnosis_confidence="HIGH",
        consistency_note="Multiple correlated sensors indicate a likely engine-related anomaly.",
        interpretation="Engine behaviour is showing a deviation from the learned healthy pattern.",
        recommendation="Review engine condition and sensor consistency. Inspect oil system.",
        timestamps=ts,
        trend_data=dict(RPM=rpm_series, oil_pressure=oilp_series, oil_temperature=oilt_series, EGT=egt_series, vibration=vib_series),
        anomaly_trend=anom_trend,
        health_timeline=health_tl,
    )


def _egt_increase() -> DashboardData:
    n = 60
    ts = _make_timestamps(n)
    rpm_series  = _smooth_series(2445, 10, n)
    oilp_series = _smooth_series(67.8, 0.5, n)
    oilt_series = _smooth_series(85.0, 0.8, n, drift=0.03)
    egt_series  = [round(612 + i * 0.65 + random.gauss(0, 3), 2) for i in range(n)]
    vib_series  = _smooth_series(0.20, 0.010, n)
    anom_trend  = [round(min(0.08 + i * 0.010 + random.uniform(0, 0.015), 0.90), 3) for i in range(n)]
    health_tl   = ["NORMAL"] * 30 + ["WARNING"] * 20 + ["ALARM"] * 10

    return dict(
        sensor_values=dict(RPM=2444.0, oil_pressure=67.8, oil_temperature=87.0, EGT=649.0, vibration=0.21),
        sensor_trends=dict(RPM="STABLE", oil_pressure="STABLE", oil_temperature="INCREASING", EGT="INCREASING", vibration="STABLE"),
        sensor_statuses=dict(RPM="NORMAL", oil_pressure="NORMAL", oil_temperature="CAUTION", EGT="WARNING", vibration="NORMAL"),
        anomaly_score=0.64,
        confidence=81.0,
        health_state="WARNING",
        diagnosis="Likely Engine Degradation",
        sensor_contributions=dict(EGT=0.82, oil_temperature=0.45, vibration=0.22, RPM=0.12, oil_pressure=0.10),
        explanation=(
            "Exhaust Gas Temperature is rising steadily, accompanied by increasing oil temperature. "
            "This pattern suggests combustion inefficiency or fuel-air mixture deviation."
        ),
        signal_consistency="HIGH",
        diagnosis_confidence="MEDIUM",
        consistency_note="EGT and oil temperature are moving together - consistent with a thermal engine event.",
        interpretation="Engine thermal behaviour is deviating from the learned healthy baseline.",
        recommendation="Monitor EGT trend closely. Consider reducing power setting if trend continues.",
        timestamps=ts,
        trend_data=dict(RPM=rpm_series, oil_pressure=oilp_series, oil_temperature=oilt_series, EGT=egt_series, vibration=vib_series),
        anomaly_trend=anom_trend,
        health_timeline=health_tl,
    )


def _vibration_increase() -> DashboardData:
    n = 60
    ts = _make_timestamps(n)
    rpm_series  = _smooth_series(2420, 20, n)
    oilp_series = _smooth_series(66.5, 0.8, n)
    oilt_series = _smooth_series(85.5, 1.0, n)
    egt_series  = _smooth_series(625, 6, n)
    vib_series  = [round(0.18 + i * 0.009 + random.gauss(0, 0.010), 3) for i in range(n)]
    anom_trend  = [round(min(0.06 + i * 0.014 + random.uniform(0, 0.02), 0.98), 3) for i in range(n)]
    health_tl   = ["NORMAL"] * 20 + ["WARNING"] * 20 + ["ALARM"] * 15 + ["EMERGENCY"] * 5

    return dict(
        sensor_values=dict(RPM=2417.0, oil_pressure=66.2, oil_temperature=86.1, EGT=627.0, vibration=0.71),
        sensor_trends=dict(RPM="DECREASING", oil_pressure="STABLE", oil_temperature="STABLE", EGT="STABLE", vibration="INCREASING"),
        sensor_statuses=dict(RPM="CAUTION", oil_pressure="NORMAL", oil_temperature="NORMAL", EGT="NORMAL", vibration="ALARM"),
        anomaly_score=0.85,
        confidence=91.0,
        health_state="ALARM",
        diagnosis="Likely Engine Degradation",
        sensor_contributions=dict(vibration=0.94, RPM=0.38, EGT=0.20, oil_pressure=0.12, oil_temperature=0.09),
        explanation=(
            "Vibration levels are rapidly increasing, which is the dominant anomaly signal. "
            "RPM is showing instability, consistent with a mechanical imbalance or bearing issue."
        ),
        signal_consistency="HIGH",
        diagnosis_confidence="HIGH",
        consistency_note="Vibration and RPM instability are correlated - consistent with a mechanical engine fault.",
        interpretation="Engine mechanical behaviour is significantly outside the healthy operating envelope.",
        recommendation="Immediate inspection recommended. Vibration at ALARM level.",
        timestamps=ts,
        trend_data=dict(RPM=rpm_series, oil_pressure=oilp_series, oil_temperature=oilt_series, EGT=egt_series, vibration=vib_series),
        anomaly_trend=anom_trend,
        health_timeline=health_tl,
    )


def _multi_sensor_degradation() -> DashboardData:
    n = 60
    ts = _make_timestamps(n)
    rpm_series  = [round(2450 - i * 0.2 + random.gauss(0, 15), 1) for i in range(n)]
    oilp_series = [round(68.5 - i * 0.10 + random.gauss(0, 0.5), 2) for i in range(n)]
    oilt_series = [round(84.0 + i * 0.04 + random.gauss(0, 0.7), 2) for i in range(n)]
    egt_series  = [round(612 + i * 0.50 + random.gauss(0, 4), 2) for i in range(n)]
    vib_series  = [round(0.18 + i * 0.008 + random.gauss(0, 0.010), 3) for i in range(n)]
    anom_trend  = [round(min(0.10 + i * 0.015 + random.uniform(0, 0.02), 0.99), 3) for i in range(n)]
    health_tl   = ["NORMAL"] * 15 + ["WARNING"] * 15 + ["ALARM"] * 20 + ["EMERGENCY"] * 10

    return dict(
        sensor_values=dict(RPM=2403.0, oil_pressure=59.8, oil_temperature=88.5, EGT=641.0, vibration=0.65),
        sensor_trends=dict(RPM="DECREASING", oil_pressure="DECREASING", oil_temperature="INCREASING", EGT="INCREASING", vibration="INCREASING"),
        sensor_statuses=dict(RPM="CAUTION", oil_pressure="ALARM", oil_temperature="WARNING", EGT="WARNING", vibration="ALARM"),
        anomaly_score=0.93,
        confidence=96.0,
        health_state="EMERGENCY",
        diagnosis="Likely Engine Degradation",
        sensor_contributions=dict(oil_pressure=0.92, vibration=0.90, EGT=0.78, RPM=0.62, oil_temperature=0.55),
        explanation=(
            "All five sensors are simultaneously deviating from the learned healthy pattern. "
            "Oil pressure is falling, vibration and EGT are rising, and RPM is dropping. "
            "This coordinated multi-sensor deviation strongly indicates a serious engine degradation event."
        ),
        signal_consistency="HIGH",
        diagnosis_confidence="HIGH",
        consistency_note="All sensors are moving in a consistent pattern indicating engine-wide degradation.",
        interpretation="CRITICAL: Engine is exhibiting coordinated multi-sensor failure signatures.",
        recommendation="EMERGENCY condition. Initiate contingency protocol. All sensors at or near alarm limits.",
        timestamps=ts,
        trend_data=dict(RPM=rpm_series, oil_pressure=oilp_series, oil_temperature=oilt_series, EGT=egt_series, vibration=vib_series),
        anomaly_trend=anom_trend,
        health_timeline=health_tl,
    )


def _sensor_only_abnormality() -> DashboardData:
    n = 60
    ts = _make_timestamps(n)
    oilp_series = [
        round(68.5 + random.choice([-1, 1]) * random.uniform(0, 8 if i > 30 else 0.5), 2)
        for i in range(n)
    ]
    rpm_series  = _smooth_series(2448, 11, n)
    oilt_series = _smooth_series(84.3, 0.6, n)
    egt_series  = _smooth_series(613, 4, n)
    vib_series  = _smooth_series(0.19, 0.009, n)
    anom_trend  = (
        [round(random.uniform(0.06, 0.15), 3) for _ in range(30)]
        + [round(random.uniform(0.30, 0.55), 3) for _ in range(30)]
    )
    health_tl   = ["NORMAL"] * 30 + ["WARNING"] * 30

    return dict(
        sensor_values=dict(RPM=2449.0, oil_pressure=74.1, oil_temperature=84.5, EGT=614.0, vibration=0.19),
        sensor_trends=dict(RPM="STABLE", oil_pressure="ERRATIC", oil_temperature="STABLE", EGT="STABLE", vibration="STABLE"),
        sensor_statuses=dict(RPM="NORMAL", oil_pressure="WARNING", oil_temperature="NORMAL", EGT="NORMAL", vibration="NORMAL"),
        anomaly_score=0.41,
        confidence=68.0,
        health_state="WARNING",
        diagnosis="Possible Sensor Issue",
        sensor_contributions=dict(oil_pressure=0.82, vibration=0.08, EGT=0.07, RPM=0.06, oil_temperature=0.05),
        explanation=(
            "Only the oil pressure sensor is showing abnormal readings, while all other sensors "
            "remain within the healthy operating range. This isolated pattern is more consistent "
            "with a sensor fault than an actual engine issue."
        ),
        signal_consistency="LOW",
        diagnosis_confidence="MEDIUM",
        consistency_note="Single sensor deviation with all others stable - consistent with a sensor fault, not engine failure.",
        interpretation="Isolated sensor anomaly detected. Engine itself may be operating normally.",
        recommendation="Verify oil pressure sensor calibration and connections before concluding engine fault.",
        timestamps=ts,
        trend_data=dict(RPM=rpm_series, oil_pressure=oilp_series, oil_temperature=oilt_series, EGT=egt_series, vibration=vib_series),
        anomaly_trend=anom_trend,
        health_timeline=health_tl,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_BUILDERS = [
    _healthy,
    _oil_pressure_degradation,
    _egt_increase,
    _vibration_increase,
    _multi_sensor_degradation,
    _sensor_only_abnormality,
]


def get_scenario_data(scenario_name: str) -> DashboardData:
    """
    Return the DashboardData dict for the given scenario name.

    PHASE 2B: Replace body of this function with a call to Phase 1 pipeline.
    Ensure the returned dict matches the DashboardData schema above.
    """
    idx = SCENARIOS.get(scenario_name, 0)
    random.seed(42 + idx)
    return _BUILDERS[idx]()


def get_all_scenario_names() -> list:
    """Return the ordered list of scenario display names."""
    return SCENARIO_LIST
