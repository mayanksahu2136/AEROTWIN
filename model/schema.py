from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class SensorObservation(BaseModel):
    RPM: float
    oil_pressure: float
    oil_temperature: float
    EGT: float
    vibration: float
    timestamp: Optional[str] = None

class SensorConfig(BaseModel):
    label: str
    unit: str
    icon: str
    color: str
    format: str

class InferenceResponse(BaseModel):
    sensor_values: Dict[str, float]
    sensor_trends: Dict[str, str]
    sensor_statuses: Dict[str, str]
    anomaly_score: float
    confidence: float
    health_state: str
    diagnosis: str
    sensor_contributions: Dict[str, float]
    explanation: str
    signal_consistency: str
    diagnosis_confidence: str
    consistency_note: str
    interpretation: str
    recommendation: str
    
    # Historical / Chart fields
    timestamps: List[str]
    trend_data: Dict[str, List[float]]
    anomaly_trend: List[float]
    health_timeline: List[str]

class ScenarioMetadata(BaseModel):
    id: int
    name: str
    description: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str

class StatusResponse(BaseModel):
    data_source: str
    inference_readiness: str
    rul_model_available: bool
