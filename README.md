# AeroTwin — AI-Powered UAV Engine Health Monitor

**Team AeroSentinels** | Phase 2A Dashboard Prototype

---

## Quick Start

### Web Dashboard (Recommended for Demo)

Simply open the HTML file in any modern browser — no server or installation required:

```
dashboard/web/index.html
```

Double-click the file, or from the command line:

```powershell
# Windows
Start-Process "dashboard\web\index.html"
```

### Web Dashboard with ML Inference API (Phase 2B)

This is the fully integrated setup that runs the local ML inference API and connects it to the dashboard.

1. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Start the FastAPI ML backend:**
   ```powershell
   uvicorn model.api:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Open the Dashboard:**
   Open `dashboard/web/index.html` in your browser. It will automatically connect to `http://127.0.0.1:8000/api/infer`.

*(Note: If the API is offline, the dashboard gracefully falls back to a deterministic JS demo mode).*

### Streamlit Dashboard (Legacy)

Requires Python 3.10+ with dependencies installed:

```bash
pip install -r model/requirements.txt
streamlit run model/dashboard/app.py
```

---

## Project Structure

```text
AEROTWIN/
├── README.md                      
├── requirements.txt               # Updated with FastAPI, Pydantic, Uvicorn
│
├── dashboard/web/                 # Static HTML dashboard
│   ├── index.html                 # Application shell
│   ├── style.css                  # Complete design system
│   ├── app.js                     # Updated to fetch from API asynchronously
│   └── data.js                    # Local fallback scenario data
│
├── model/                         # ML Pipeline & Backend
│   ├── api.py                     # FastAPI endpoints (/api/infer, etc.)
│   ├── inference.py               # Model Adapter Layer (Graceful demo fallback)
│   ├── schema.py                  # Canonical Data Contract (Pydantic)
│   ├── requirements.txt           
│   └── dashboard/                 # Shared Streamlit & Python logic
│       └── demo_data.py           # Canonical scenario logic
│
└── tests/
    └── test_api.py                # Automated pytest suite for API
```

## Phase 2B Integration Status

**1. Confirmed working functionality:**
- FastAPI REST backend serving the canonical data contract.
- ML adapter layer (`model.inference.ModelAdapter`) configured for safe routing.
- Frontend asynchronously fetches inference results and handles fallbacks.
- Shared Pydantic data schemas.
- Pytest test suite for validation and scenario endpoints.

**2. Available trained models:**
- ⚠ **None found in workspace.** The adapter currently operates in DEMO FALLBACK mode. 

**3. Integration Plan for Future Models:**
To connect a trained model (e.g. Scikit-Learn or PyTorch) when ready:
1. Place the serialized artifact (e.g., `model.pkl`) in a `models/` directory.
2. Edit `model/inference.py`:
   - Uncomment the loading logic in `_load_models()`.
   - Implement `_real_inference(self, obs)`.
   - Validate and normalize inputs against the `SensorObservation` schema.
3. The API and Frontend will automatically detect `models_loaded = True` and transition from Demo mode to real inference mode.

## Features

### Dashboard Sections

| Section | Status | Description |
|---------|--------|-------------|
| Overview | ✅ Complete | Health hero, sensor cards, diagnosis, trend charts, anomaly timeline |
| Digital Twin | ✅ Complete | Interactive engine schematic with component health mapping |
| Live Telemetry | ✅ Complete | Per-sensor historical traces with multi-select |
| Anomaly Detection | ✅ Complete | Score timeline with threshold lines, health state timeline |
| Explainable AI | ✅ Complete | Contribution bars, signal consistency, diagnosis reasoning |
| Predictive Maintenance | ⚠ Prototype | No RUL model — honest prototype panel with degradation trends |
| Alerts & Diagnostics | ✅ Complete | Scenario-derived event log with severity filtering |
| Settings / About | ✅ Complete | Configuration, data contract, sensor units |

### Demo Scenarios

1. **Healthy** — All sensors nominal, low anomaly score
2. **Gradual Oil-Pressure Degradation** — Correlated oil pressure drop with vibration increase
3. **EGT Increase** — Rising exhaust gas temperature with thermal cascade
4. **Vibration Increase** — Rapid mechanical vibration spike at ALARM level
5. **Multi-Sensor Degradation** — Coordinated 5-sensor failure at EMERGENCY level
6. **Sensor-Only Abnormality** — Isolated erratic oil pressure (likely sensor fault)

### Data Units (Canonical)

| Sensor | Unit |
|--------|------|
| RPM | rpm |
| Oil Pressure | bar |
| Oil Temperature | °C |
| EGT | °C |
| Vibration | g |

Health States: `NORMAL` → `WARNING` → `ALARM` → `EMERGENCY`

---

## Important Notes

- **All data is synthetic.** This is a Phase 2A UI prototype using mock data.
- **No ML pipeline is connected.** Phase 2B will integrate the Phase 1 trained model.
- **No RUL model exists.** The Predictive Maintenance section honestly labels this.
- **Not certified for flight operations** or safety-critical decisions.

## Phase 2B Integration

The `data.js` file documents the data contract. To connect real model outputs:

1. Replace `getScenarioData()` with a `fetch()` to the Phase 1 API
2. Ensure the returned JSON matches the `DashboardData` schema (see `data.js` header)
3. Update the data-source indicator from "Demo" to "Connected"

---

*AeroTwin Phase 2A • AeroSentinels*
