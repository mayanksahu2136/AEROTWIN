/**
 * AeroTwin — Canonical Scenario Data
 * ====================================
 * Ported faithfully from model/dashboard/demo_data.py
 * 
 * Units (from model/dashboard/styles.py SENSOR_CONFIG):
 *   RPM             — rpm
 *   Oil Pressure    — bar
 *   Oil Temperature — °C
 *   EGT             — °C
 *   Vibration       — g
 * 
 * Health states: NORMAL | WARNING | ALARM | EMERGENCY
 * Sensor statuses: NORMAL | CAUTION | WARNING | ALARM
 * Trends: STABLE | INCREASING | DECREASING | ERRATIC
 * 
 * PHASE 2B: Replace getScenarioData() with a fetch to the Phase 1 pipeline.
 */

// ─── Sensor metadata ─────────────────────────────────────────────────────────

const SENSOR_CONFIG = {
    RPM: {
        label: "RPM",
        unit: "rpm",
        icon: "⚙",
        color: "#00c8ff",
        format: v => v.toFixed(0),
    },
    oil_pressure: {
        label: "Oil Pressure",
        unit: "bar",
        icon: "🛢",
        color: "#ff9500",
        format: v => v.toFixed(1),
    },
    oil_temperature: {
        label: "Oil Temp",
        unit: "°C",
        icon: "🌡",
        color: "#ff5722",
        format: v => v.toFixed(1),
    },
    EGT: {
        label: "EGT",
        unit: "°C",
        icon: "🔥",
        color: "#ff1744",
        format: v => v.toFixed(0),
    },
    vibration: {
        label: "Vibration",
        unit: "g",
        icon: "〰",
        color: "#aa00ff",
        format: v => v.toFixed(2),
    },
};

const SENSOR_ORDER = ["RPM", "oil_pressure", "oil_temperature", "EGT", "vibration"];

// ─── Thresholds for anomaly chart ────────────────────────────────────────────

const ANOMALY_THRESHOLDS = [
    { value: 0.35, label: "WARNING",   color: "#ffb300" },
    { value: 0.65, label: "ALARM",     color: "#ff5722" },
    { value: 0.85, label: "EMERGENCY", color: "#ff1744" },
];

// ─── Health state styling ────────────────────────────────────────────────────

const STATE_COLORS = {
    NORMAL:    "#00e676",
    WARNING:   "#ffb300",
    ALARM:     "#ff5722",
    EMERGENCY: "#ff1744",
};

const STATE_BG_COLORS = {
    NORMAL:    "#004d25",
    WARNING:   "#4d3600",
    ALARM:     "#4d1a0a",
    EMERGENCY: "#4d0013",
};

const STATE_ICONS = {
    NORMAL:    "●",
    WARNING:   "⚠",
    ALARM:     "🔴",
    EMERGENCY: "🚨",
};

const SENSOR_STATUS_COLORS = {
    NORMAL:  "#00e676",
    CAUTION: "#ffd740",
    WARNING: "#ffb300",
    ALARM:   "#ff5722",
};

const TREND_ICONS = {
    STABLE:     "→",
    INCREASING: "↑",
    DECREASING: "↓",
    ERRATIC:    "↯",
};

const CONSISTENCY_COLORS = {
    HIGH:   "#00e676",
    MEDIUM: "#ffb300",
    LOW:    "#ff5722",
};

// ─── Deterministic series generators ─────────────────────────────────────────

function seededRandom(seed) {
    let s = seed;
    return function() {
        s = (s * 1664525 + 1013904223) & 0xFFFFFFFF;
        return (s >>> 0) / 0xFFFFFFFF;
    };
}

function seededGauss(rng) {
    let spare;
    let hasSpare = false;
    return function(mean, stddev) {
        if (hasSpare) {
            hasSpare = false;
            return spare * stddev + mean;
        }
        let u, v, s;
        do {
            u = rng() * 2 - 1;
            v = rng() * 2 - 1;
            s = u * u + v * v;
        } while (s >= 1 || s === 0);
        s = Math.sqrt(-2.0 * Math.log(s) / s);
        spare = v * s;
        hasSpare = true;
        return (u * s) * stddev + mean;
    };
}

function makeTimestamps(n = 60) {
    const now = new Date(2026, 9, 6, 14, 0, 0); // Oct 6, 2026 14:00:00
    const step = 10000; // 10 seconds
    const stamps = [];
    for (let i = 0; i < n; i++) {
        const t = new Date(now.getTime() - step * (n - i - 1));
        stamps.push(t.toISOString().replace('T', ' ').substring(0, 19));
    }
    return stamps;
}

function smoothSeries(base, noise, n, drift, rng) {
    const gauss = seededGauss(rng);
    const series = [];
    let val = base;
    for (let i = 0; i < n; i++) {
        val += drift + gauss(0, noise);
        series.push(parseFloat(val.toFixed(2)));
    }
    return series;
}

// ─── Scenario builders (faithful port from demo_data.py) ─────────────────────

function buildHealthy(rng) {
    const n = 60;
    const gauss = seededGauss(rng);
    const ts = makeTimestamps(n);

    return {
        sensor_values: { RPM: 2451.0, oil_pressure: 68.5, oil_temperature: 84.2, EGT: 613.0, vibration: 0.18 },
        sensor_trends: { RPM: "STABLE", oil_pressure: "STABLE", oil_temperature: "STABLE", EGT: "STABLE", vibration: "STABLE" },
        sensor_statuses: { RPM: "NORMAL", oil_pressure: "NORMAL", oil_temperature: "NORMAL", EGT: "NORMAL", vibration: "NORMAL" },
        anomaly_score: 0.11,
        confidence: 94.0,
        health_state: "NORMAL",
        diagnosis: "No Anomaly",
        sensor_contributions: { oil_pressure: 0.15, vibration: 0.12, EGT: 0.10, RPM: 0.08, oil_temperature: 0.06 },
        explanation: "All sensor signals are within the learned healthy operating range. No deviations detected.",
        signal_consistency: "HIGH",
        diagnosis_confidence: "HIGH",
        consistency_note: "All sensors are in agreement. Engine behaviour matches healthy baseline.",
        interpretation: "Engine is operating normally. All parameters are within expected bounds.",
        recommendation: "No action required. Continue normal operation.",
        timestamps: ts,
        trend_data: {
            RPM: smoothSeries(2450, 12, n, 0, rng),
            oil_pressure: smoothSeries(68.5, 0.4, n, 0, rng),
            oil_temperature: smoothSeries(84.2, 0.6, n, 0, rng),
            EGT: smoothSeries(612, 4, n, 0, rng),
            vibration: smoothSeries(0.18, 0.008, n, 0, rng),
        },
        anomaly_trend: Array.from({ length: n }, () => parseFloat((rng() * 0.13 + 0.05).toFixed(3))),
        health_timeline: Array(n).fill("NORMAL"),
    };
}

function buildOilPressureDegradation(rng) {
    const n = 60;
    const gauss = seededGauss(rng);
    const ts = makeTimestamps(n);

    const oilp = [];
    for (let i = 0; i < n; i++) oilp.push(parseFloat((68.5 - i * 0.12 + gauss(0, 0.4)).toFixed(2)));

    return {
        sensor_values: { RPM: 2428.0, oil_pressure: 62.4, oil_temperature: 86.5, EGT: 619.0, vibration: 0.24 },
        sensor_trends: { RPM: "STABLE", oil_pressure: "DECREASING", oil_temperature: "INCREASING", EGT: "STABLE", vibration: "INCREASING" },
        sensor_statuses: { RPM: "NORMAL", oil_pressure: "WARNING", oil_temperature: "CAUTION", EGT: "NORMAL", vibration: "CAUTION" },
        anomaly_score: 0.72,
        confidence: 87.0,
        health_state: "WARNING",
        diagnosis: "Likely Engine Degradation",
        sensor_contributions: { oil_pressure: 0.88, vibration: 0.62, EGT: 0.35, RPM: 0.18, oil_temperature: 0.14 },
        explanation: "Oil pressure is steadily decreasing while vibration is gradually increasing. These are correlated deviations from the learned healthy pattern, suggesting an engine-related issue rather than a single sensor fault.",
        signal_consistency: "HIGH",
        diagnosis_confidence: "HIGH",
        consistency_note: "Multiple correlated sensors indicate a likely engine-related anomaly.",
        interpretation: "Engine behaviour is showing a deviation from the learned healthy pattern.",
        recommendation: "Review engine condition and sensor consistency. Inspect oil system.",
        timestamps: ts,
        trend_data: {
            RPM: smoothSeries(2430, 15, n, 0, rng),
            oil_pressure: oilp,
            oil_temperature: smoothSeries(86.0, 1.0, n, 0.02, rng),
            EGT: smoothSeries(618, 5, n, 0, rng),
            vibration: smoothSeries(0.22, 0.012, n, 0.0005, rng),
        },
        anomaly_trend: Array.from({ length: n }, (_, i) => parseFloat(Math.min(0.05 + i * 0.012 + rng() * 0.02, 0.95).toFixed(3))),
        health_timeline: Array(25).fill("NORMAL").concat(Array(25).fill("WARNING"), Array(10).fill("ALARM")),
    };
}

function buildEGTIncrease(rng) {
    const n = 60;
    const gauss = seededGauss(rng);
    const ts = makeTimestamps(n);

    const egt = [];
    for (let i = 0; i < n; i++) egt.push(parseFloat((612 + i * 0.65 + gauss(0, 3)).toFixed(2)));

    return {
        sensor_values: { RPM: 2444.0, oil_pressure: 67.8, oil_temperature: 87.0, EGT: 649.0, vibration: 0.21 },
        sensor_trends: { RPM: "STABLE", oil_pressure: "STABLE", oil_temperature: "INCREASING", EGT: "INCREASING", vibration: "STABLE" },
        sensor_statuses: { RPM: "NORMAL", oil_pressure: "NORMAL", oil_temperature: "CAUTION", EGT: "WARNING", vibration: "NORMAL" },
        anomaly_score: 0.64,
        confidence: 81.0,
        health_state: "WARNING",
        diagnosis: "Likely Engine Degradation",
        sensor_contributions: { EGT: 0.82, oil_temperature: 0.45, vibration: 0.22, RPM: 0.12, oil_pressure: 0.10 },
        explanation: "Exhaust Gas Temperature is rising steadily, accompanied by increasing oil temperature. This pattern suggests combustion inefficiency or fuel-air mixture deviation.",
        signal_consistency: "HIGH",
        diagnosis_confidence: "MEDIUM",
        consistency_note: "EGT and oil temperature are moving together — consistent with a thermal engine event.",
        interpretation: "Engine thermal behaviour is deviating from the learned healthy baseline.",
        recommendation: "Monitor EGT trend closely. Consider reducing power setting if trend continues.",
        timestamps: ts,
        trend_data: {
            RPM: smoothSeries(2445, 10, n, 0, rng),
            oil_pressure: smoothSeries(67.8, 0.5, n, 0, rng),
            oil_temperature: smoothSeries(85.0, 0.8, n, 0.03, rng),
            EGT: egt,
            vibration: smoothSeries(0.20, 0.010, n, 0, rng),
        },
        anomaly_trend: Array.from({ length: n }, (_, i) => parseFloat(Math.min(0.08 + i * 0.010 + rng() * 0.015, 0.90).toFixed(3))),
        health_timeline: Array(30).fill("NORMAL").concat(Array(20).fill("WARNING"), Array(10).fill("ALARM")),
    };
}

function buildVibrationIncrease(rng) {
    const n = 60;
    const gauss = seededGauss(rng);
    const ts = makeTimestamps(n);

    const vib = [];
    for (let i = 0; i < n; i++) vib.push(parseFloat((0.18 + i * 0.009 + gauss(0, 0.010)).toFixed(3)));

    return {
        sensor_values: { RPM: 2417.0, oil_pressure: 66.2, oil_temperature: 86.1, EGT: 627.0, vibration: 0.71 },
        sensor_trends: { RPM: "DECREASING", oil_pressure: "STABLE", oil_temperature: "STABLE", EGT: "STABLE", vibration: "INCREASING" },
        sensor_statuses: { RPM: "CAUTION", oil_pressure: "NORMAL", oil_temperature: "NORMAL", EGT: "NORMAL", vibration: "ALARM" },
        anomaly_score: 0.85,
        confidence: 91.0,
        health_state: "ALARM",
        diagnosis: "Likely Engine Degradation",
        sensor_contributions: { vibration: 0.94, RPM: 0.38, EGT: 0.20, oil_pressure: 0.12, oil_temperature: 0.09 },
        explanation: "Vibration levels are rapidly increasing, which is the dominant anomaly signal. RPM is showing instability, consistent with a mechanical imbalance or bearing issue.",
        signal_consistency: "HIGH",
        diagnosis_confidence: "HIGH",
        consistency_note: "Vibration and RPM instability are correlated — consistent with a mechanical engine fault.",
        interpretation: "Engine mechanical behaviour is significantly outside the healthy operating envelope.",
        recommendation: "Immediate inspection recommended. Vibration at ALARM level.",
        timestamps: ts,
        trend_data: {
            RPM: smoothSeries(2420, 20, n, 0, rng),
            oil_pressure: smoothSeries(66.5, 0.8, n, 0, rng),
            oil_temperature: smoothSeries(85.5, 1.0, n, 0, rng),
            EGT: smoothSeries(625, 6, n, 0, rng),
            vibration: vib,
        },
        anomaly_trend: Array.from({ length: n }, (_, i) => parseFloat(Math.min(0.06 + i * 0.014 + rng() * 0.02, 0.98).toFixed(3))),
        health_timeline: Array(20).fill("NORMAL").concat(Array(20).fill("WARNING"), Array(15).fill("ALARM"), Array(5).fill("EMERGENCY")),
    };
}

function buildMultiSensorDegradation(rng) {
    const n = 60;
    const gauss = seededGauss(rng);
    const ts = makeTimestamps(n);

    const rpm = [], oilp = [], oilt = [], egt = [], vib = [];
    for (let i = 0; i < n; i++) {
        rpm.push(parseFloat((2450 - i * 0.2 + gauss(0, 15)).toFixed(1)));
        oilp.push(parseFloat((68.5 - i * 0.10 + gauss(0, 0.5)).toFixed(2)));
        oilt.push(parseFloat((84.0 + i * 0.04 + gauss(0, 0.7)).toFixed(2)));
        egt.push(parseFloat((612 + i * 0.50 + gauss(0, 4)).toFixed(2)));
        vib.push(parseFloat((0.18 + i * 0.008 + gauss(0, 0.010)).toFixed(3)));
    }

    return {
        sensor_values: { RPM: 2403.0, oil_pressure: 59.8, oil_temperature: 88.5, EGT: 641.0, vibration: 0.65 },
        sensor_trends: { RPM: "DECREASING", oil_pressure: "DECREASING", oil_temperature: "INCREASING", EGT: "INCREASING", vibration: "INCREASING" },
        sensor_statuses: { RPM: "CAUTION", oil_pressure: "ALARM", oil_temperature: "WARNING", EGT: "WARNING", vibration: "ALARM" },
        anomaly_score: 0.93,
        confidence: 96.0,
        health_state: "EMERGENCY",
        diagnosis: "Likely Engine Degradation",
        sensor_contributions: { oil_pressure: 0.92, vibration: 0.90, EGT: 0.78, RPM: 0.62, oil_temperature: 0.55 },
        explanation: "All five sensors are simultaneously deviating from the learned healthy pattern. Oil pressure is falling, vibration and EGT are rising, and RPM is dropping. This coordinated multi-sensor deviation strongly indicates a serious engine degradation event.",
        signal_consistency: "HIGH",
        diagnosis_confidence: "HIGH",
        consistency_note: "All sensors are moving in a consistent pattern indicating engine-wide degradation.",
        interpretation: "CRITICAL: Engine is exhibiting coordinated multi-sensor failure signatures.",
        recommendation: "EMERGENCY condition. Initiate contingency protocol. All sensors at or near alarm limits.",
        timestamps: ts,
        trend_data: { RPM: rpm, oil_pressure: oilp, oil_temperature: oilt, EGT: egt, vibration: vib },
        anomaly_trend: Array.from({ length: n }, (_, i) => parseFloat(Math.min(0.10 + i * 0.015 + rng() * 0.02, 0.99).toFixed(3))),
        health_timeline: Array(15).fill("NORMAL").concat(Array(15).fill("WARNING"), Array(20).fill("ALARM"), Array(10).fill("EMERGENCY")),
    };
}

function buildSensorOnlyAbnormality(rng) {
    const n = 60;
    const gauss = seededGauss(rng);
    const ts = makeTimestamps(n);

    const oilp = [];
    for (let i = 0; i < n; i++) {
        const spike = i > 30 ? (rng() > 0.5 ? 1 : -1) * rng() * 8 : (rng() > 0.5 ? 1 : -1) * rng() * 0.5;
        oilp.push(parseFloat((68.5 + spike).toFixed(2)));
    }

    return {
        sensor_values: { RPM: 2449.0, oil_pressure: 74.1, oil_temperature: 84.5, EGT: 614.0, vibration: 0.19 },
        sensor_trends: { RPM: "STABLE", oil_pressure: "ERRATIC", oil_temperature: "STABLE", EGT: "STABLE", vibration: "STABLE" },
        sensor_statuses: { RPM: "NORMAL", oil_pressure: "WARNING", oil_temperature: "NORMAL", EGT: "NORMAL", vibration: "NORMAL" },
        anomaly_score: 0.41,
        confidence: 68.0,
        health_state: "WARNING",
        diagnosis: "Possible Sensor Issue",
        sensor_contributions: { oil_pressure: 0.82, vibration: 0.08, EGT: 0.07, RPM: 0.06, oil_temperature: 0.05 },
        explanation: "Only the oil pressure sensor is showing abnormal readings, while all other sensors remain within the healthy operating range. This isolated pattern is more consistent with a sensor fault than an actual engine issue.",
        signal_consistency: "LOW",
        diagnosis_confidence: "MEDIUM",
        consistency_note: "Single sensor deviation with all others stable — consistent with a sensor fault, not engine failure.",
        interpretation: "Isolated sensor anomaly detected. Engine itself may be operating normally.",
        recommendation: "Verify oil pressure sensor calibration and connections before concluding engine fault.",
        timestamps: ts,
        trend_data: {
            RPM: smoothSeries(2448, 11, n, 0, rng),
            oil_pressure: oilp,
            oil_temperature: smoothSeries(84.3, 0.6, n, 0, rng),
            EGT: smoothSeries(613, 4, n, 0, rng),
            vibration: smoothSeries(0.19, 0.009, n, 0, rng),
        },
        anomaly_trend: Array.from({ length: 30 }, () => parseFloat((rng() * 0.09 + 0.06).toFixed(3)))
            .concat(Array.from({ length: 30 }, () => parseFloat((rng() * 0.25 + 0.30).toFixed(3)))),
        health_timeline: Array(30).fill("NORMAL").concat(Array(30).fill("WARNING")),
    };
}

// ─── Public API ──────────────────────────────────────────────────────────────

const SCENARIO_BUILDERS = [
    buildHealthy,
    buildOilPressureDegradation,
    buildEGTIncrease,
    buildVibrationIncrease,
    buildMultiSensorDegradation,
    buildSensorOnlyAbnormality,
];

const SCENARIO_NAMES = [
    "Healthy",
    "Gradual Oil-Pressure Degradation",
    "EGT Increase",
    "Vibration Increase",
    "Multi-Sensor Degradation",
    "Sensor-Only Abnormality",
];

/**
 * Returns the DashboardData object for a given scenario index.
 * Uses a deterministic seed so repeated calls return identical data.
 */
function getScenarioData(index) {
    const rng = seededRandom(42 + index);
    return SCENARIO_BUILDERS[index](rng);
}
