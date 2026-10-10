import pytest
from fastapi.testclient import TestClient
import math

from model.api import app
from model.inference import adapter
from model.schema import SensorObservation

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "model_loaded" in data

def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "data_source" in data
    assert "rul_model_available" in data

def test_scenarios_endpoint():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    assert data[0]["name"] == "Healthy"

def test_inference_fallback():
    # Because we have no real models, this should fall back to demo scenario 1
    obs = {
        "RPM": 2450.0,
        "oil_pressure": 68.5,
        "oil_temperature": 84.0,
        "EGT": 612.0,
        "vibration": 0.18
    }
    response = client.post("/api/infer?scenario_id=1", json=obs)
    assert response.status_code == 200
    data = response.json()
    assert data["health_state"] in ["NORMAL", "WARNING", "ALARM", "EMERGENCY"]
    assert "anomaly_score" in data
    assert "sensor_contributions" in data
    
def test_inference_invalid_input():
    # Test rejection of NaN values
    obs = SensorObservation(
        RPM=float('nan'),
        oil_pressure=68.5,
        oil_temperature=84.0,
        EGT=612.0,
        vibration=0.18
    )
    # The adapter should catch this
    assert adapter.validate_observation(obs) is False

def test_missing_fields_rejected():
    obs = {
        "RPM": 2450.0,
        "oil_pressure": 68.5
        # Missing others
    }
    response = client.post("/api/infer?scenario_id=1", json=obs)
    assert response.status_code == 422  # Pydantic validation error

def test_rul_unavailable():
    # Verify the status correctly reports no RUL
    response = client.get("/api/status")
    data = response.json()
    assert data["rul_model_available"] is False
