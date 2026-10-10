from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .schema import SensorObservation, InferenceResponse, ScenarioMetadata, HealthResponse, StatusResponse
from .inference import adapter
from .dashboard.demo_data import get_all_scenario_names

app = FastAPI(
    title="AeroTwin ML Inference API",
    description="API connecting the AeroTwin dashboard to the underlying ML pipeline.",
    version="Phase 2B"
)

# Enable CORS for the static frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """
    Check if the API and models are running.
    """
    return HealthResponse(
        status="ok",
        model_loaded=adapter.models_loaded,
        version="Phase 2B"
    )

@app.get("/api/status", response_model=StatusResponse)
def get_status():
    """
    Data-source and inference readiness status.
    """
    status_data = adapter.get_status()
    return StatusResponse(**status_data)

@app.get("/api/scenarios", response_model=List[ScenarioMetadata])
def get_scenarios():
    """
    Get the list of supported demo scenarios.
    """
    names = get_all_scenario_names()
    return [ScenarioMetadata(id=idx, name=name, description="") for idx, name in enumerate(names)]

@app.post("/api/infer", response_model=InferenceResponse)
def run_inference(obs: SensorObservation, scenario_id: int = None):
    """
    Validate an observation and return inference outputs.
    If real ML models are missing, it falls back to demo scenarios.
    """
    try:
        response = adapter.infer(obs, scenario_id=scenario_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

# Allow running from command line easily
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("model.api:app", host="0.0.0.0", port=8000, reload=True)
