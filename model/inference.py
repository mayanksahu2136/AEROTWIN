import logging
import math
from typing import Dict, Any, Optional

# Attempt to import real models if they exist in the future
try:
    import joblib
    import torch
    import tensorflow as tf
except ImportError:
    pass

from .schema import SensorObservation, InferenceResponse
from .dashboard.demo_data import get_scenario_data, get_all_scenario_names

logger = logging.getLogger(__name__)

class ModelAdapter:
    """
    ML Inference Adapter.
    Provides a stable interface between the dashboard and the actual ML pipeline.
    """
    def __init__(self):
        self.models_loaded = False
        self.anomaly_detector = None
        self.health_classifier = None
        self.rul_model = None
        self._load_models()
        
    def _load_models(self):
        """
        Attempt to load trained model artifacts.
        Currently, no trained models exist in the workspace.
        This provides a documented interface for when Phase 1 models are ready.
        """
        # Example of loading a future scikit-learn model:
        # try:
        #     self.anomaly_detector = joblib.load('models/anomaly_isolation_forest.pkl')
        #     self.models_loaded = True
        # except FileNotFoundError:
        #     logger.warning("Anomaly detector model not found. Using demo fallback.")
        
        # Example of loading a PyTorch RUL model:
        # try:
        #     self.rul_model = torch.load('models/rul_lstm.pt')
        # except FileNotFoundError:
        #     logger.warning("RUL model not found.")
        
        self.models_loaded = False
        logger.info("No trained models found in workspace. Adapter running in DEMO mode.")

    def validate_observation(self, obs: SensorObservation) -> bool:
        """
        Validate sensor observation input to handle NaN or infinite values safely.
        """
        for field, value in obs.model_dump().items():
            if isinstance(value, float):
                if math.isnan(value) or math.isinf(value):
                    return False
        return True

    def infer(self, obs: SensorObservation, scenario_id: Optional[int] = None) -> InferenceResponse:
        """
        Main inference method.
        
        If real models are loaded, preprocess the observation and run inference.
        If models are absent, uses the requested demo scenario as a graceful fallback.
        """
        if not self.validate_observation(obs):
            raise ValueError("Invalid sensor observation containing NaN or infinite values.")

        if self.models_loaded:
            return self._real_inference(obs)
        else:
            return self._demo_inference(scenario_id)

    def _real_inference(self, obs: SensorObservation) -> InferenceResponse:
        """
        Placeholder for real inference logic.
        Will validate inputs, normalize, run through self.anomaly_detector, 
        and build the InferenceResponse matching the canonical data contract.
        """
        raise NotImplementedError("Real inference is not fully implemented because models are missing.")

    def _demo_inference(self, scenario_id: Optional[int]) -> InferenceResponse:
        """
        Graceful fallback using demo scenarios when real models are unavailable.
        """
        if scenario_id is None:
            scenario_id = 0  # Default to Healthy
            
        scenario_names = get_all_scenario_names()
        if scenario_id < 0 or scenario_id >= len(scenario_names):
            raise ValueError(f"Unsupported scenario_id: {scenario_id}")
            
        data = get_scenario_data(scenario_id)
        
        return InferenceResponse(**data)
        
    def get_status(self) -> Dict[str, Any]:
        """
        Status for the dashboard API to identify whether real ML is running.
        """
        return {
            "data_source": "ML Pipeline" if self.models_loaded else "Demo (Synthetic)",
            "inference_readiness": "Ready" if self.models_loaded else "Fallback (Demo Mode)",
            "rul_model_available": self.rul_model is not None
        }

# Singleton instance
adapter = ModelAdapter()
