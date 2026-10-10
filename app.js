/**
 * AeroTwin — Dashboard Application Logic
 * ========================================
 * Single-page application controller for the AeroTwin digital-twin dashboard.
 * 
 * Architecture:
 *   data.js   → Canonical scenario data (ported from demo_data.py)
 *   style.css → Design system
 *   app.js    → This file: navigation, rendering, chart management
 */

// ═══════════════════════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════════════════════

let currentScenarioIndex = 0;
let currentPage = "overview";
let selectedOverviewSensors = ["RPM", "oil_pressure", "vibration"];
let selectedTelemetrySensors = ["RPM", "oil_pressure", "vibration"];
let alertSeverityFilter = "ALL";
let selectedTwinComponent = null;

// Chart instances (destroy before re-creating)
const charts = {};

// Cached scenario data
let scenarioData = null;

// ═══════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener("DOMContentLoaded", () => {
    initScenarioSelect();
    initNavigation();
    initSidebarToggle();
    initClock();
    initResetButton();
    loadScenario(0);
});

function initScenarioSelect() {
    const select = document.getElementById("scenarioSelect");
    SCENARIO_NAMES.forEach((name, i) => {
        const opt = document.createElement("option");
        opt.value = i;
        opt.textContent = name;
        select.appendChild(opt);
    });
    select.addEventListener("change", e => {
        loadScenario(parseInt(e.target.value));
    });
}

function initNavigation() {
    document.querySelectorAll(".nav-item[data-page]").forEach(item => {
        item.addEventListener("click", e => {
            e.preventDefault();
            navigateTo(item.dataset.page);
            // Close mobile sidebar
            document.getElementById("sidebar").classList.remove("mobile-open");
            document.getElementById("sidebarOverlay").classList.remove("visible");
        });
    });

    document.getElementById("brandLink").addEventListener("click", e => {
        e.preventDefault();
        navigateTo("overview");
    });
}

function initSidebarToggle() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const toggle = document.getElementById("sidebarToggle");

    toggle.addEventListener("click", () => {
        const isMobile = window.innerWidth <= 900;
        if (isMobile) {
            sidebar.classList.toggle("mobile-open");
            overlay.classList.toggle("visible");
        } else {
            sidebar.classList.toggle("collapsed");
        }
    });

    overlay.addEventListener("click", () => {
        sidebar.classList.remove("mobile-open");
        overlay.classList.remove("visible");
    });
}

function initClock() {
    function tick() {
        const now = new Date();
        const h = String(now.getHours()).padStart(2, "0");
        const m = String(now.getMinutes()).padStart(2, "0");
        const s = String(now.getSeconds()).padStart(2, "0");
        document.getElementById("topbarClock").textContent = `${h}:${m}:${s}`;
    }
    tick();
    setInterval(tick, 1000);
}

function initResetButton() {
    document.getElementById("resetBtn").addEventListener("click", () => {
        document.getElementById("scenarioSelect").value = 0;
        loadScenario(0);
        navigateTo("overview");
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════════════════

const PAGE_LABELS = {
    "overview":     "Overview",
    "digital-twin": "Digital Twin",
    "telemetry":    "Live Telemetry",
    "anomaly":      "Anomaly Detection",
    "xai":          "Explainable AI",
    "predictive":   "Predictive Maintenance",
    "alerts":       "Alerts & Diagnostics",
    "settings":     "Settings / About",
};

function navigateTo(page) {
    currentPage = page;

    // Update nav items
    document.querySelectorAll(".nav-item[data-page]").forEach(item => {
        item.classList.toggle("active", item.dataset.page === page);
    });

    // Switch page views
    document.querySelectorAll(".page-view").forEach(view => {
        view.classList.toggle("active", view.id === `page-${page}`);
    });

    // Update breadcrumb
    document.getElementById("crumbActive").textContent = PAGE_LABELS[page] || page;

    // Render page-specific content
    renderCurrentPage();
}

// ═══════════════════════════════════════════════════════════════════════════
// SCENARIO LOADING
// ═══════════════════════════════════════════════════════════════════════════

async function loadScenario(index) {
    currentScenarioIndex = index;
    
    // Update topbar scenario label
    document.getElementById("topbarScenario").textContent =
        `SCENARIO: ${SCENARIO_NAMES[index]} (Loading...)`;

    // Attempt to fetch from API (Stage 3 & 5 ML Integration)
    try {
        // Send a dummy observation representing current state (in a real app, this comes from live telemetry)
        const dummyObs = {
            RPM: 2450.0,
            oil_pressure: 68.5,
            oil_temperature: 84.0,
            EGT: 612.0,
            vibration: 0.18
        };
        const response = await fetch(`http://127.0.0.1:8000/api/infer?scenario_id=${index}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dummyObs)
        });
        if (!response.ok) throw new Error("API response not ok");
        scenarioData = await response.json();
        
        // Update settings status
        fetch('http://127.0.0.1:8000/api/status')
            .then(res => res.json())
            .then(status => {
                const el = document.getElementById("settingDataSource");
                if(el) el.textContent = status.data_source;
            }).catch(e => {});
            
    } catch (e) {
        console.warn("ML API unavailable, falling back to local JS demo data.", e);
        scenarioData = getScenarioData(index);
        const el = document.getElementById("settingDataSource");
        if(el) el.textContent = "Demo (Synthetic - JS Fallback)";
    }

    document.getElementById("topbarScenario").textContent =
        `SCENARIO: ${SCENARIO_NAMES[index]}`;

    // Render all content for current page
    renderCurrentPage();
}

function renderCurrentPage() {
    if (!scenarioData) return;

    // Always render overview content (it has persistent charts)
    renderOverview();

    switch (currentPage) {
        case "digital-twin": renderDigitalTwin(); break;
        case "telemetry":    renderTelemetry(); break;
        case "anomaly":      renderAnomalyPage(); break;
        case "xai":          renderXaiPage(); break;
        case "predictive":   renderPredictivePage(); break;
        case "alerts":       renderAlertsPage(); break;
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// OVERVIEW PAGE
// ═══════════════════════════════════════════════════════════════════════════

function renderOverview() {
    const d = scenarioData;

    // ── Hero + Diagnosis ──
    const stateColor = STATE_COLORS[d.health_state] || "#00c8ff";
    const stateBg = STATE_BG_COLORS[d.health_state] || "#161925";
    const stateIcon = STATE_ICONS[d.health_state] || "●";

    const scoreColor = d.anomaly_score < 0.35 ? "#00e676" :
                       d.anomaly_score < 0.65 ? "#ffb300" :
                       d.anomaly_score < 0.85 ? "#ff5722" : "#ff1744";

    const diagIcons = {
        "No Anomaly": "✓",
        "Possible Sensor Issue": "⚠",
        "Likely Engine Degradation": "⬡",
    };

    document.getElementById("overviewHeroGrid").innerHTML = `
        <div class="hero-panel" style="border-left: 3px solid ${stateColor}">
            <div class="hero-hex">⬡</div>
            <div class="hero-label">// ENGINE HEALTH STATUS</div>
            <div class="hero-state" style="background:${stateBg}; border:1px solid ${stateColor}; color:${stateColor}; box-shadow:0 0 16px ${stateColor}30">
                ${stateIcon}&nbsp;${d.health_state}
            </div>
            <div class="hero-metrics">
                <div class="hero-metric" data-tooltip="Anomaly detection score from 0 (normal) to 1 (anomalous)">
                    <div class="hm-label">Anomaly Score</div>
                    <div class="hm-value" style="color:${scoreColor}">${d.anomaly_score.toFixed(2)}</div>
                    <div class="gauge-bar"><div class="gauge-fill" style="width:${Math.round(d.anomaly_score * 100)}%; background:${scoreColor}"></div></div>
                </div>
                <div class="hero-metric" data-tooltip="Prototype confidence indicator — not a calibrated probability">
                    <div class="hm-label">AI Confidence</div>
                    <div class="hm-value" style="color:#00c8ff">${d.confidence.toFixed(0)}%</div>
                    <div class="gauge-bar"><div class="gauge-fill" style="width:${Math.round(d.confidence)}%; background:#00c8ff"></div></div>
                </div>
            </div>
            <div class="conf-note">
                ⚠ Prototype confidence indicator — not a calibrated probability. All values are DEMO/MOCK data.
            </div>
        </div>
        <div>
            <div class="diag-panel" style="background:var(--bg-panel); border-left:3px solid ${stateColor}">
                <div class="diag-header">// ENGINE DIAGNOSIS</div>
                <div class="diag-value" style="color:${stateColor}">${diagIcons[d.diagnosis] || "⬡"}&nbsp;${d.diagnosis}</div>
                <div class="diag-expl">${d.explanation}</div>
            </div>
            <div class="interp-panel" style="background:var(--bg-panel); border-left:3px solid ${stateColor}">
                <div class="interp-header">// CURRENT INTERPRETATION</div>
                <div class="interp-text">${d.interpretation}</div>
                <div class="recom-label">Suggested Action</div>
                <div class="recom-text" style="color:${stateColor}">${d.recommendation}</div>
            </div>
        </div>
    `;

    // ── Sensor Cards ──
    renderSensorCards("overviewSensors");

    // ── XAI Section ──
    renderXaiSection("overviewXaiGrid");

    // ── Sensor Checks for Trend Chart ──
    renderSensorCheckboxes("overviewSensorChecks", selectedOverviewSensors, sensors => {
        selectedOverviewSensors = sensors;
        renderOverviewTrendChart();
    });

    // ── Charts ──
    renderOverviewTrendChart();
    renderAnomalyChart("overviewAnomalyChart", 280);
    renderHealthTimelineChart("overviewHealthChart", 180);
}

function renderSensorCards(containerId) {
    const d = scenarioData;
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = SENSOR_ORDER.map(key => {
        const cfg = SENSOR_CONFIG[key];
        const val = d.sensor_values[key] || 0;
        const trend = d.sensor_trends[key] || "STABLE";
        const status = d.sensor_statuses[key] || "NORMAL";
        const color = SENSOR_STATUS_COLORS[status] || "#00e676";
        const tIcon = TREND_ICONS[trend] || "→";
        const formatted = cfg.format(val);

        // Sparkline data
        const trendArr = d.trend_data[key] || [];
        const sparkId = `spark-${containerId}-${key}`;

        return `
            <div class="sensor-card" style="border-top:2px solid ${cfg.color}"
                 data-tooltip="${cfg.label}: ${formatted} ${cfg.unit} — ${trend}">
                <div class="sc-icon-label">
                    <span class="sc-icon">${cfg.icon}</span>
                    <span class="sc-label">${cfg.label}</span>
                </div>
                <div class="sc-value">${formatted}<span class="sc-unit">${cfg.unit}</span></div>
                <div class="sc-sparkline-container"><canvas id="${sparkId}" height="28"></canvas></div>
                <div class="sc-trend">${tIcon} ${trend}</div>
                <div class="sc-status" style="color:${color}; background:${color}15; border:1px solid ${color}40">${status}</div>
            </div>
        `;
    }).join("");

    // Render sparklines
    SENSOR_ORDER.forEach(key => {
        const sparkId = `spark-${containerId}-${key}`;
        const canvas = document.getElementById(sparkId);
        if (!canvas) return;
        const trendArr = d.trend_data[key] || [];
        if (trendArr.length === 0) return;

        // Take last 20 points for sparkline
        const last20 = trendArr.slice(-20);
        const cfg = SENSOR_CONFIG[key];

        destroyChart(sparkId);
        charts[sparkId] = new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                labels: last20.map((_, i) => i),
                datasets: [{
                    data: last20,
                    borderColor: cfg.color,
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: {
                    x: { display: false },
                    y: { display: false },
                },
                animation: { duration: 300 },
            },
        });
    });
}

function renderXaiSection(containerId) {
    const d = scenarioData;
    const container = document.getElementById(containerId);
    if (!container) return;

    const stateColor = STATE_COLORS[d.health_state] || "#00c8ff";
    const consistColor = CONSISTENCY_COLORS[d.signal_consistency] || "#00c8ff";
    const diagConfColor = CONSISTENCY_COLORS[d.diagnosis_confidence] || "#00c8ff";

    // XAI contribution bars
    const sorted = Object.entries(d.sensor_contributions).sort((a, b) => b[1] - a[1]);
    const barsHtml = sorted.map(([key, weight]) => {
        const cfg = SENSOR_CONFIG[key] || { label: key, color: "#00c8ff" };
        const pct = Math.round(weight * 100);
        return `
            <div class="xai-bar-row">
                <div class="xai-bar-label">${cfg.label}</div>
                <div class="xai-bar-track">
                    <div class="xai-bar-fill" style="width:${pct}%; background:linear-gradient(90deg, ${cfg.color}cc, ${cfg.color})"></div>
                </div>
                <div class="xai-bar-pct" style="color:${cfg.color}">${pct}%</div>
            </div>
        `;
    }).join("");

    container.innerHTML = `
        <div class="xai-panel">
            <div class="xai-header">// WHY IS THE ENGINE FLAGGED?</div>
            <div class="xai-subheader">Sensor contribution to anomaly score (relative, demo values)</div>
            ${barsHtml}
            <div class="xai-expl">${d.explanation}</div>
        </div>
        <div class="consist-panel">
            <div class="consist-header">// ENGINE SIGNAL CONSISTENCY</div>
            <div class="consist-diag">${d.diagnosis}</div>
            <div class="consist-row">
                <div class="consist-item">
                    <div class="ci-label">Sensor Agreement</div>
                    <div class="ci-value" style="color:${consistColor}">${d.signal_consistency}</div>
                </div>
                <div class="consist-item">
                    <div class="ci-label">Diagnosis Confidence</div>
                    <div class="ci-value" style="color:${diagConfColor}">${d.diagnosis_confidence}</div>
                </div>
            </div>
            <div class="consist-note">${d.consistency_note}</div>
        </div>
    `;
}

function renderSensorCheckboxes(containerId, selectedArr, onChange) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = SENSOR_ORDER.map(key => {
        const cfg = SENSOR_CONFIG[key];
        const checked = selectedArr.includes(key);
        return `
            <label class="sensor-check ${checked ? "checked" : ""}" data-sensor="${key}">
                <input type="checkbox" ${checked ? "checked" : ""}>
                <span class="sensor-check-dot" style="background:${cfg.color}"></span>
                ${cfg.label}
            </label>
        `;
    }).join("");

    container.querySelectorAll(".sensor-check").forEach(label => {
        label.addEventListener("click", e => {
            e.preventDefault();
            const key = label.dataset.sensor;
            const cb = label.querySelector("input");
            cb.checked = !cb.checked;
            label.classList.toggle("checked", cb.checked);

            const newSelection = [];
            container.querySelectorAll(".sensor-check").forEach(l => {
                if (l.querySelector("input").checked) newSelection.push(l.dataset.sensor);
            });
            onChange(newSelection);
        });
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// CHARTS
// ═══════════════════════════════════════════════════════════════════════════

function destroyChart(id) {
    if (charts[id]) {
        charts[id].destroy();
        delete charts[id];
    }
}

const CHART_COLORS = {
    bg_panel: "#11141f",
    bg_card: "#161925",
    border: "#1e2535",
    text_secondary: "#8a95a8",
    text_muted: "#4a5568",
};

function chartBaseOptions(height) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 400 },
        plugins: {
            legend: {
                display: true,
                labels: {
                    color: CHART_COLORS.text_secondary,
                    font: { family: "'Inter', sans-serif", size: 10 },
                    boxWidth: 10,
                    padding: 12,
                },
            },
            tooltip: {
                backgroundColor: CHART_COLORS.bg_card,
                borderColor: "#00c8ff",
                borderWidth: 1,
                titleColor: "#e8ecf4",
                bodyColor: "#8a95a8",
                titleFont: { family: "'JetBrains Mono', monospace", size: 11 },
                bodyFont: { family: "'Inter', sans-serif", size: 11 },
                padding: 10,
                cornerRadius: 3,
            },
        },
        scales: {
            x: {
                grid: { color: CHART_COLORS.border },
                ticks: { color: CHART_COLORS.text_muted, font: { size: 9 }, maxTicksLimit: 10 },
            },
            y: {
                grid: { color: CHART_COLORS.border },
                ticks: { color: CHART_COLORS.text_muted, font: { size: 9 } },
            },
        },
    };
}

// ── Overview Trend Chart ──

function renderOverviewTrendChart() {
    const d = scenarioData;
    const id = "overviewTrendChart";
    destroyChart(id);

    const canvas = document.getElementById(id);
    if (!canvas) return;

    const datasets = selectedOverviewSensors.map(key => {
        const cfg = SENSOR_CONFIG[key];
        return {
            label: `${cfg.label} (${cfg.unit})`,
            data: d.trend_data[key] || [],
            borderColor: cfg.color,
            backgroundColor: `${cfg.color}15`,
            borderWidth: 1.5,
            pointRadius: 0,
            pointHitRadius: 8,
            fill: false,
            tension: 0.3,
            yAxisID: `y-${key}`,
        };
    });

    // Build y-axes
    const scales = {
        x: {
            grid: { color: CHART_COLORS.border },
            ticks: {
                color: CHART_COLORS.text_muted,
                font: { size: 9 },
                maxTicksLimit: 10,
                callback: function(value, index) {
                    return d.timestamps[index] ? d.timestamps[index].split(" ")[1] : "";
                },
            },
        },
    };

    selectedOverviewSensors.forEach((key, idx) => {
        const cfg = SENSOR_CONFIG[key];
        scales[`y-${key}`] = {
            type: "linear",
            position: idx % 2 === 0 ? "left" : "right",
            grid: { drawOnChartArea: idx === 0, color: CHART_COLORS.border },
            ticks: { color: cfg.color, font: { size: 9, family: "'JetBrains Mono', monospace" } },
            title: { display: true, text: `${cfg.label} (${cfg.unit})`, color: cfg.color, font: { size: 9 } },
        };
    });

    charts[id] = new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
            labels: d.timestamps.map(t => t.split(" ")[1]),
            datasets,
        },
        options: {
            ...chartBaseOptions(),
            scales,
            interaction: { mode: "index", intersect: false },
        },
    });
}

// ── Anomaly Chart ──

function renderAnomalyChart(canvasId, height) {
    const d = scenarioData;
    destroyChart(canvasId);

    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const thresholdLines = ANOMALY_THRESHOLDS.map(t => ({
        type: "line",
        yMin: t.value,
        yMax: t.value,
        borderColor: t.color,
        borderWidth: 1,
        borderDash: [4, 3],
        label: {
            display: true,
            content: t.label,
            position: "end",
            color: t.color,
            font: { size: 9, family: "'JetBrains Mono', monospace" },
            backgroundColor: "transparent",
        },
    }));

    charts[canvasId] = new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
            labels: d.timestamps.map(t => t.split(" ")[1]),
            datasets: [{
                label: "Anomaly Score",
                data: d.anomaly_trend,
                borderColor: "#ffb300",
                backgroundColor: "rgba(255,179,0,0.08)",
                borderWidth: 1.5,
                pointRadius: 0,
                pointHitRadius: 8,
                fill: true,
                tension: 0.3,
            }],
        },
        options: {
            ...chartBaseOptions(),
            scales: {
                x: {
                    grid: { color: CHART_COLORS.border },
                    ticks: { color: CHART_COLORS.text_muted, font: { size: 9 }, maxTicksLimit: 10 },
                },
                y: {
                    min: 0, max: 1.05,
                    grid: { color: CHART_COLORS.border },
                    ticks: { color: CHART_COLORS.text_muted, font: { size: 9 } },
                    title: { display: true, text: "SCORE", color: CHART_COLORS.text_muted, font: { size: 10 } },
                },
            },
            plugins: {
                ...chartBaseOptions().plugins,
                legend: { display: false },
                annotation: thresholdLines.length > 0 ? { annotations: thresholdLines } : undefined,
            },
        },
    });

    // Draw threshold lines manually since annotation plugin may not be loaded
    drawThresholdLines(canvas, canvasId);
}

function drawThresholdLines(canvas, chartId) {
    // We'll use a custom plugin approach
    const chart = charts[chartId];
    if (!chart) return;

    const originalDraw = chart.draw.bind(chart);
    chart.draw = function() {
        originalDraw();
        const ctx = chart.ctx;
        const yScale = chart.scales.y;
        const xScale = chart.scales.x;

        ANOMALY_THRESHOLDS.forEach(t => {
            const y = yScale.getPixelForValue(t.value);
            ctx.save();
            ctx.setLineDash([4, 3]);
            ctx.strokeStyle = t.color;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(xScale.left, y);
            ctx.lineTo(xScale.right, y);
            ctx.stroke();

            ctx.fillStyle = t.color;
            ctx.font = "9px 'JetBrains Mono', monospace";
            ctx.textAlign = "right";
            ctx.fillText(t.label, xScale.right, y - 3);
            ctx.restore();
        });
    };
    chart.draw();
}

// ── Health Timeline Chart ──

function renderHealthTimelineChart(canvasId, height) {
    const d = scenarioData;
    destroyChart(canvasId);

    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const stateNum = { NORMAL: 0, WARNING: 1, ALARM: 2, EMERGENCY: 3 };
    const yVals = d.health_timeline.map(s => stateNum[s] !== undefined ? stateNum[s] : 0);
    const barColors = d.health_timeline.map(s => STATE_COLORS[s] || "#00e676");

    charts[canvasId] = new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
            labels: d.timestamps.map(t => t.split(" ")[1]),
            datasets: [{
                data: yVals.map(() => 1),
                backgroundColor: barColors,
                borderWidth: 0,
                barPercentage: 1.0,
                categoryPercentage: 1.0,
            }],
        },
        options: {
            ...chartBaseOptions(),
            plugins: {
                ...chartBaseOptions().plugins,
                legend: { display: false },
                tooltip: {
                    ...chartBaseOptions().plugins.tooltip,
                    callbacks: {
                        title: (items) => d.timestamps[items[0].dataIndex] || "",
                        label: (item) => d.health_timeline[item.dataIndex] || "",
                    },
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: CHART_COLORS.text_muted, font: { size: 9 }, maxTicksLimit: 10 },
                    stacked: true,
                },
                y: {
                    min: -0.5, max: 3.5,
                    grid: { color: CHART_COLORS.border },
                    ticks: {
                        stepSize: 1,
                        color: CHART_COLORS.text_secondary,
                        font: { size: 9, family: "'JetBrains Mono', monospace" },
                        callback: v => ["NORMAL", "WARNING", "ALARM", "EMERGENCY"][v] || "",
                    },
                    stacked: true,
                },
            },
        },
    });

    // Manually position bars using 'base'
    // Chart.js stacked bar doesn't have a 'base' per-bar, so we use a floating bar approach
    // Re-do with floating bars:
    destroyChart(canvasId);
    charts[canvasId] = new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
            labels: d.timestamps.map(t => t.split(" ")[1]),
            datasets: [{
                data: yVals.map(v => [v, v + 0.8]),
                backgroundColor: barColors,
                borderWidth: 0,
                barPercentage: 1.0,
                categoryPercentage: 1.0,
            }],
        },
        options: {
            ...chartBaseOptions(),
            indexAxis: "x",
            plugins: {
                ...chartBaseOptions().plugins,
                legend: { display: false },
                tooltip: {
                    ...chartBaseOptions().plugins.tooltip,
                    callbacks: {
                        title: (items) => d.timestamps[items[0].dataIndex] || "",
                        label: (item) => d.health_timeline[item.dataIndex] || "",
                    },
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: CHART_COLORS.text_muted, font: { size: 8 }, maxTicksLimit: 8 },
                },
                y: {
                    min: -0.5, max: 3.8,
                    grid: { color: CHART_COLORS.border },
                    ticks: {
                        stepSize: 1,
                        color: CHART_COLORS.text_secondary,
                        font: { size: 9, family: "'JetBrains Mono', monospace" },
                        callback: v => ["NORMAL", "WARNING", "ALARM", "EMERGENCY"][v] || "",
                    },
                },
            },
        },
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// DIGITAL TWIN PAGE
// ═══════════════════════════════════════════════════════════════════════════

function renderDigitalTwin() {
    const d = scenarioData;

    // Engine schematic SVG
    const schematicEl = document.getElementById("engineSchematic");
    schematicEl.innerHTML = buildEngineSVG(d);

    // Add click handlers to components
    schematicEl.querySelectorAll(".engine-component").forEach(comp => {
        comp.addEventListener("click", () => {
            selectedTwinComponent = comp.dataset.sensor;
            renderTwinDetails();
            // Highlight selected
            schematicEl.querySelectorAll(".engine-component").forEach(c => c.classList.remove("selected"));
            comp.classList.add("selected");
        });
    });

    renderTwinDetails();
    renderTwinLegend();
}

function buildEngineSVG(d) {
    // Create a schematic representation of a UAV piston engine
    // Components: Cylinder/RPM, Oil System, Cooling/Temp, Exhaust/EGT, Vibration/Mount

    const componentData = [
        { key: "RPM", label: "Cylinders / RPM", x: 200, y: 120, w: 140, h: 80 },
        { key: "oil_pressure", label: "Oil System", x: 60, y: 240, w: 120, h: 60 },
        { key: "oil_temperature", label: "Oil Cooler", x: 60, y: 320, w: 120, h: 60 },
        { key: "EGT", label: "Exhaust System", x: 360, y: 120, w: 120, h: 80 },
        { key: "vibration", label: "Engine Mount", x: 200, y: 340, w: 140, h: 50 },
    ];

    const statusColor = (key) => {
        const s = d.sensor_statuses[key] || "NORMAL";
        return SENSOR_STATUS_COLORS[s] || "#00e676";
    };

    const statusGlow = (key) => {
        const s = d.sensor_statuses[key] || "NORMAL";
        if (s === "NORMAL") return "none";
        const col = SENSOR_STATUS_COLORS[s];
        return `0 0 12px ${col}60`;
    };

    let svg = `<svg viewBox="0 0 540 420" class="engine-svg" xmlns="http://www.w3.org/2000/svg">`;

    // Background grid
    svg += `<defs>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e2535" stroke-width="0.5"/>
        </pattern>
    </defs>
    <rect width="540" height="420" fill="#11141f" rx="4"/>
    <rect width="540" height="420" fill="url(#grid)"/>`;

    // Title
    svg += `<text x="270" y="30" text-anchor="middle" fill="#4a5568" font-family="'JetBrains Mono', monospace" font-size="10" letter-spacing="0.15em">UAV PISTON ENGINE — COMPONENT HEALTH</text>`;

    // Connection lines
    svg += `<line x1="270" y1="200" x2="120" y2="240" stroke="#2a3550" stroke-width="1" stroke-dasharray="4,3"/>`;
    svg += `<line x1="270" y1="200" x2="120" y2="320" stroke="#2a3550" stroke-width="1" stroke-dasharray="4,3"/>`;
    svg += `<line x1="340" y1="160" x2="360" y2="160" stroke="#2a3550" stroke-width="1" stroke-dasharray="4,3"/>`;
    svg += `<line x1="270" y1="200" x2="270" y2="340" stroke="#2a3550" stroke-width="1" stroke-dasharray="4,3"/>`;

    // Components
    componentData.forEach(comp => {
        const col = statusColor(comp.key);
        const cfg = SENSOR_CONFIG[comp.key];
        const val = d.sensor_values[comp.key] || 0;
        const formatted = cfg.format(val);

        svg += `
            <g class="engine-component" data-sensor="${comp.key}" style="cursor:pointer">
                <rect x="${comp.x}" y="${comp.y}" width="${comp.w}" height="${comp.h}"
                      rx="4" fill="#161925" stroke="${col}" stroke-width="1.5"
                      style="filter:drop-shadow(${statusGlow(comp.key)})"/>
                <text x="${comp.x + comp.w/2}" y="${comp.y + 18}" text-anchor="middle"
                      fill="${col}" font-family="'JetBrains Mono', monospace" font-size="8"
                      letter-spacing="0.1em">${comp.label.toUpperCase()}</text>
                <text x="${comp.x + comp.w/2}" y="${comp.y + comp.h/2 + 8}" text-anchor="middle"
                      fill="#e8ecf4" font-family="'JetBrains Mono', monospace" font-size="14"
                      font-weight="600">${formatted}</text>
                <text x="${comp.x + comp.w/2}" y="${comp.y + comp.h - 8}" text-anchor="middle"
                      fill="#4a5568" font-family="'Inter', sans-serif" font-size="8">${cfg.unit}</text>
            </g>
        `;
    });

    // Central engine body outline
    svg += `<rect x="180" y="100" width="180" height="210" rx="8" fill="none" stroke="#2a3550" stroke-width="1" stroke-dasharray="8,4"/>`;
    svg += `<text x="270" y="290" text-anchor="middle" fill="#2a3550" font-family="'JetBrains Mono', monospace" font-size="8">ENGINE BLOCK</text>`;

    svg += `</svg>`;
    return svg;
}

function renderTwinDetails() {
    const d = scenarioData;
    const container = document.getElementById("twinDetails");

    if (!selectedTwinComponent) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⬡</div>
                <h3>Select a Component</h3>
                <p>Click on an engine component in the schematic to view its details, current reading, status, and trend.</p>
            </div>
        `;
        return;
    }

    const key = selectedTwinComponent;
    const cfg = SENSOR_CONFIG[key];
    const val = d.sensor_values[key] || 0;
    const trend = d.sensor_trends[key] || "STABLE";
    const status = d.sensor_statuses[key] || "NORMAL";
    const contribution = d.sensor_contributions[key] || 0;
    const color = SENSOR_STATUS_COLORS[status] || "#00e676";

    container.innerHTML = `
        <div class="twin-detail-card" style="border-left:3px solid ${cfg.color}">
            <div class="twin-detail-label">Component</div>
            <div class="twin-detail-value">${cfg.icon} ${cfg.label}</div>
        </div>
        <div class="twin-detail-card">
            <div class="twin-detail-label">Current Reading</div>
            <div class="twin-detail-value">${cfg.format(val)} <span style="color:var(--text-muted); font-size:0.7rem">${cfg.unit}</span></div>
        </div>
        <div class="twin-detail-card">
            <div class="twin-detail-label">Status</div>
            <div class="twin-detail-value" style="color:${color}">${status}</div>
        </div>
        <div class="twin-detail-card">
            <div class="twin-detail-label">Trend</div>
            <div class="twin-detail-value">${TREND_ICONS[trend] || "→"} ${trend}</div>
        </div>
        <div class="twin-detail-card">
            <div class="twin-detail-label">Anomaly Contribution</div>
            <div class="twin-detail-value" style="color:${cfg.color}">${Math.round(contribution * 100)}%</div>
            <div class="gauge-bar" style="margin-top:0.4rem">
                <div class="gauge-fill" style="width:${Math.round(contribution * 100)}%; background:${cfg.color}"></div>
            </div>
        </div>
    `;
}

function renderTwinLegend() {
    const container = document.getElementById("twinLegend");
    const states = [
        { label: "NORMAL", color: "#00e676" },
        { label: "CAUTION", color: "#ffd740" },
        { label: "WARNING", color: "#ffb300" },
        { label: "ALARM", color: "#ff5722" },
    ];
    container.innerHTML = states.map(s => `
        <div class="legend-item">
            <div class="legend-swatch" style="background:${s.color}"></div>
            ${s.label}
        </div>
    `).join("");
}

// ═══════════════════════════════════════════════════════════════════════════
// LIVE TELEMETRY PAGE
// ═══════════════════════════════════════════════════════════════════════════

function renderTelemetry() {
    const d = scenarioData;

    // Sensor checkboxes
    renderSensorCheckboxes("telemetrySensorChecks", selectedTelemetrySensors, sensors => {
        selectedTelemetrySensors = sensors;
        renderTelemetryCharts();
    });

    renderTelemetryCharts();
}

function renderTelemetryCharts() {
    const d = scenarioData;
    const container = document.getElementById("telemetryChartsContainer");
    if (!container) return;

    container.innerHTML = selectedTelemetrySensors.map(key => {
        const cfg = SENSOR_CONFIG[key];
        const chartId = `telemetry-chart-${key}`;
        return `
            <div class="panel" style="margin-bottom:1rem">
                <div class="chart-header">
                    <div class="chart-title">${cfg.icon} ${cfg.label} (${cfg.unit})</div>
                </div>
                <div class="chart-container" style="height:200px">
                    <canvas id="${chartId}"></canvas>
                </div>
            </div>
        `;
    }).join("");

    // Render each chart
    selectedTelemetrySensors.forEach(key => {
        const chartId = `telemetry-chart-${key}`;
        const cfg = SENSOR_CONFIG[key];
        destroyChart(chartId);

        const canvas = document.getElementById(chartId);
        if (!canvas) return;

        charts[chartId] = new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                labels: d.timestamps.map(t => t.split(" ")[1]),
                datasets: [{
                    label: `${cfg.label} (${cfg.unit})`,
                    data: d.trend_data[key] || [],
                    borderColor: cfg.color,
                    backgroundColor: `${cfg.color}10`,
                    borderWidth: 1.5,
                    pointRadius: 0,
                    pointHitRadius: 8,
                    fill: true,
                    tension: 0.3,
                }],
            },
            options: {
                ...chartBaseOptions(),
                plugins: {
                    ...chartBaseOptions().plugins,
                    legend: { display: false },
                },
                scales: {
                    x: {
                        grid: { color: CHART_COLORS.border },
                        ticks: { color: CHART_COLORS.text_muted, font: { size: 9 }, maxTicksLimit: 10 },
                    },
                    y: {
                        grid: { color: CHART_COLORS.border },
                        ticks: { color: cfg.color, font: { size: 9, family: "'JetBrains Mono', monospace" } },
                        title: { display: true, text: cfg.unit, color: cfg.color, font: { size: 9 } },
                    },
                },
                interaction: { mode: "index", intersect: false },
            },
        });
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// ANOMALY DETECTION PAGE
// ═══════════════════════════════════════════════════════════════════════════

function renderAnomalyPage() {
    const d = scenarioData;

    renderAnomalyChart("anomalyFullChart", 300);
    renderHealthTimelineChart("anomalyHealthChart", 200);

    // Summary panel
    const stateColor = STATE_COLORS[d.health_state] || "#00c8ff";
    const scoreColor = d.anomaly_score < 0.35 ? "#00e676" :
                       d.anomaly_score < 0.65 ? "#ffb300" :
                       d.anomaly_score < 0.85 ? "#ff5722" : "#ff1744";

    document.getElementById("anomalySummaryPanel").innerHTML = `
        <div class="chart-title" style="margin-bottom:1rem">ANOMALY SUMMARY</div>
        <div style="margin-bottom:0.8rem">
            <div class="ci-label">Current Score</div>
            <div style="font-family:var(--font-mono); font-size:2rem; font-weight:600; color:${scoreColor}">${d.anomaly_score.toFixed(2)}</div>
        </div>
        <div style="margin-bottom:0.8rem">
            <div class="ci-label">Health State</div>
            <div style="font-family:var(--font-mono); font-size:1rem; font-weight:600; color:${stateColor}">${STATE_ICONS[d.health_state]} ${d.health_state}</div>
        </div>
        <div style="margin-bottom:0.8rem">
            <div class="ci-label">Interpretation</div>
            <div style="font-size:0.78rem; color:var(--text-secondary); line-height:1.5">${d.interpretation}</div>
        </div>
        <div>
            <div class="ci-label">Threshold Reference</div>
            ${ANOMALY_THRESHOLDS.map(t => `
                <div style="display:flex; align-items:center; gap:0.5rem; margin-top:0.3rem">
                    <div style="width:8px; height:8px; border-radius:1px; background:${t.color}"></div>
                    <span style="font-family:var(--font-mono); font-size:0.65rem; color:${t.color}">${t.label}: ${t.value}</span>
                </div>
            `).join("")}
        </div>
    `;
}

// ═══════════════════════════════════════════════════════════════════════════
// EXPLAINABLE AI PAGE
// ═══════════════════════════════════════════════════════════════════════════

function renderXaiPage() {
    const d = scenarioData;

    renderXaiSection("xaiFullGrid");

    // Technical details panel
    const panel = document.getElementById("xaiTechnicalPanel");
    if (!panel) return;

    const sorted = Object.entries(d.sensor_contributions).sort((a, b) => b[1] - a[1]);
    const topSensor = sorted[0];
    const topCfg = SENSOR_CONFIG[topSensor[0]] || { label: topSensor[0] };

    panel.innerHTML = `
        <div class="chart-title" style="margin-bottom:0.75rem">TECHNICAL DETAILS</div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem">
            <div>
                <div class="ci-label">Most Influential Sensor</div>
                <div style="font-family:var(--font-mono); font-size:0.9rem; font-weight:600; color:var(--text-primary); margin-top:0.25rem">
                    ${topCfg.label} (${Math.round(topSensor[1] * 100)}%)
                </div>
            </div>
            <div>
                <div class="ci-label">Signal Consistency</div>
                <div style="font-family:var(--font-mono); font-size:0.9rem; font-weight:600; color:${CONSISTENCY_COLORS[d.signal_consistency]}; margin-top:0.25rem">
                    ${d.signal_consistency}
                </div>
            </div>
            <div>
                <div class="ci-label">Diagnosis Confidence</div>
                <div style="font-family:var(--font-mono); font-size:0.9rem; font-weight:600; color:${CONSISTENCY_COLORS[d.diagnosis_confidence]}; margin-top:0.25rem">
                    ${d.diagnosis_confidence}
                </div>
            </div>
            <div>
                <div class="ci-label">Anomaly Score</div>
                <div style="font-family:var(--font-mono); font-size:0.9rem; font-weight:600; color:var(--text-primary); margin-top:0.25rem">
                    ${d.anomaly_score.toFixed(2)}
                </div>
            </div>
        </div>
        <div style="margin-top:1rem; padding-top:0.75rem; border-top:1px solid var(--border)">
            <div class="ci-label">Interpretation Note</div>
            <div style="font-size:0.78rem; color:var(--text-secondary); line-height:1.55; margin-top:0.3rem">
                Sensor contribution values represent the <em>relative weight</em> each sensor has in the anomaly detection model's
                output for this scenario. They are <strong>not</strong> causal proof, Shapley values, or feature importance from a
                specific algorithm. These are demonstration values that illustrate the concept of explainable AI for engine health monitoring.
            </div>
        </div>
    `;
}

// ═══════════════════════════════════════════════════════════════════════════
// PREDICTIVE MAINTENANCE PAGE
// ═══════════════════════════════════════════════════════════════════════════

function renderPredictivePage() {
    const d = scenarioData;
    const container = document.getElementById("predictiveContent");
    if (!container) return;

    // Show degradation trends
    const degradingSensors = SENSOR_ORDER.filter(key => {
        const trend = d.sensor_trends[key];
        return trend === "INCREASING" || trend === "DECREASING";
    });

    let html = `
        <div class="section-header">
            <div class="sec-label">Current Degradation Indicators</div>
            <div class="sec-subtitle">Based on sensor trend analysis (demo data)</div>
        </div>
    `;

    if (degradingSensors.length === 0) {
        html += `
            <div class="panel">
                <div class="empty-state">
                    <div class="empty-icon">✓</div>
                    <h3>No Active Degradation</h3>
                    <p>All sensors are showing stable trends in the current scenario. No degradation indicators to report.</p>
                </div>
            </div>
        `;
    } else {
        html += `<div class="grid-2">`;
        degradingSensors.forEach(key => {
            const cfg = SENSOR_CONFIG[key];
            const trend = d.sensor_trends[key];
            const status = d.sensor_statuses[key] || "NORMAL";
            const color = SENSOR_STATUS_COLORS[status] || "#00e676";
            const chartId = `pred-chart-${key}`;

            html += `
                <div class="panel">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem">
                        <div class="chart-title">${cfg.icon} ${cfg.label} — ${trend}</div>
                        <div class="sc-status" style="color:${color}; background:${color}15; border:1px solid ${color}40">${status}</div>
                    </div>
                    <div class="chart-container" style="height:160px">
                        <canvas id="${chartId}"></canvas>
                    </div>
                </div>
            `;
        });
        html += `</div>`;
    }

    // Maintenance recommendations
    html += `
        <div style="height:1rem"></div>
        <div class="section-header">
            <div class="sec-label">Maintenance Recommendation</div>
            <div class="sec-subtitle">Based on current scenario — not a certified maintenance instruction</div>
        </div>
        <div class="panel" style="border-left:3px solid ${STATE_COLORS[d.health_state] || "#00c8ff"}">
            <div style="font-family:var(--font-mono); font-size:0.62rem; color:var(--text-muted); letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.4rem">// RECOMMENDED ACTION</div>
            <div style="font-size:0.85rem; color:${STATE_COLORS[d.health_state]}; line-height:1.55; margin-bottom:0.6rem">${d.recommendation}</div>
            <div style="font-size:0.75rem; color:var(--text-muted); font-style:italic">
                ⚠ This is a demonstration recommendation based on synthetic scenario data.
                Actual maintenance decisions require qualified engineering assessment.
            </div>
        </div>
    `;

    container.innerHTML = html;

    // Render degradation charts
    degradingSensors.forEach(key => {
        const chartId = `pred-chart-${key}`;
        const cfg = SENSOR_CONFIG[key];
        destroyChart(chartId);

        const canvas = document.getElementById(chartId);
        if (!canvas) return;

        charts[chartId] = new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                labels: d.timestamps.map(t => t.split(" ")[1]),
                datasets: [{
                    data: d.trend_data[key] || [],
                    borderColor: cfg.color,
                    backgroundColor: `${cfg.color}10`,
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.3,
                }],
            },
            options: {
                ...chartBaseOptions(),
                plugins: { ...chartBaseOptions().plugins, legend: { display: false } },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: CHART_COLORS.text_muted, font: { size: 8 }, maxTicksLimit: 6 },
                    },
                    y: {
                        grid: { color: CHART_COLORS.border },
                        ticks: { color: cfg.color, font: { size: 8 } },
                    },
                },
            },
        });
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// ALERTS PAGE
// ═══════════════════════════════════════════════════════════════════════════

function renderAlertsPage() {
    const d = scenarioData;

    // Generate alerts from scenario data
    const alerts = generateAlerts(d);

    // Render filter buttons
    const filtersEl = document.getElementById("alertFilters");
    const severities = ["ALL", "EMERGENCY", "ALARM", "WARNING", "NORMAL"];
    filtersEl.innerHTML = severities.map(sev => `
        <button class="chart-btn ${alertSeverityFilter === sev ? "active" : ""}" data-severity="${sev}">
            ${sev}
        </button>
    `).join("");

    filtersEl.querySelectorAll(".chart-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            alertSeverityFilter = btn.dataset.severity;
            renderAlertsPage();
        });
    });

    // Filter alerts
    const filtered = alertSeverityFilter === "ALL" ? alerts :
        alerts.filter(a => a.severity === alertSeverityFilter);

    // Render table rows
    const tbody = document.getElementById("alertsBody");
    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding:2rem">No alerts matching the selected filter.</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map(alert => {
        const color = STATE_COLORS[alert.severity] || "#8a95a8";
        return `
            <tr>
                <td><span class="severity-badge" style="color:${color}; background:${color}15; border:1px solid ${color}40">${alert.severity}</span></td>
                <td style="font-family:var(--font-mono); font-size:0.72rem">${alert.time}</td>
                <td>${alert.sensor}</td>
                <td>${alert.description}</td>
                <td style="font-size:0.72rem; color:var(--text-muted)">${alert.action}</td>
            </tr>
        `;
    }).join("");
}

function generateAlerts(d) {
    const alerts = [];
    const ts = d.timestamps;

    // Generate alerts based on health timeline transitions
    let prevState = d.health_timeline[0];
    for (let i = 1; i < d.health_timeline.length; i++) {
        const state = d.health_timeline[i];
        if (state !== prevState) {
            alerts.push({
                severity: state,
                time: ts[i],
                sensor: "System",
                description: `Health state changed: ${prevState} → ${state}`,
                action: state === "EMERGENCY" ? "Initiate contingency protocol" :
                        state === "ALARM" ? "Immediate inspection required" :
                        state === "WARNING" ? "Monitor closely" : "Resume normal ops",
            });
        }
        prevState = state;
    }

    // Generate alerts for sensor status issues
    SENSOR_ORDER.forEach(key => {
        const status = d.sensor_statuses[key];
        const cfg = SENSOR_CONFIG[key];
        const trend = d.sensor_trends[key];

        if (status === "ALARM") {
            alerts.push({
                severity: "ALARM",
                time: ts[ts.length - 1],
                sensor: cfg.label,
                description: `${cfg.label} at ALARM level: ${cfg.format(d.sensor_values[key])} ${cfg.unit}`,
                action: "Inspect immediately",
            });
        } else if (status === "WARNING") {
            alerts.push({
                severity: "WARNING",
                time: ts[ts.length - 1],
                sensor: cfg.label,
                description: `${cfg.label} in WARNING state: ${cfg.format(d.sensor_values[key])} ${cfg.unit}, trend: ${trend}`,
                action: "Monitor and evaluate",
            });
        } else if (status === "CAUTION") {
            alerts.push({
                severity: "WARNING",
                time: ts[ts.length - 1],
                sensor: cfg.label,
                description: `${cfg.label} showing CAUTION: trend ${trend}`,
                action: "Watch for further deviation",
            });
        }
    });

    // Sort by severity then time
    const severityOrder = { EMERGENCY: 0, ALARM: 1, WARNING: 2, NORMAL: 3 };
    alerts.sort((a, b) => (severityOrder[a.severity] || 9) - (severityOrder[b.severity] || 9));

    // Add a "demo generated" note
    if (alerts.length === 0) {
        alerts.push({
            severity: "NORMAL",
            time: ts[ts.length - 1],
            sensor: "System",
            description: "No anomalies detected. All systems nominal.",
            action: "Continue normal operation",
        });
    }

    return alerts;
}

// ═══════════════════════════════════════════════════════════════════════════
// KEYBOARD NAVIGATION
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener("keydown", e => {
    // Escape closes mobile sidebar
    if (e.key === "Escape") {
        document.getElementById("sidebar").classList.remove("mobile-open");
        document.getElementById("sidebarOverlay").classList.remove("visible");
    }
});
