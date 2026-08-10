import os
import json
import joblib
from sklearn.ensemble import RandomForestClassifier
from .. import config

class ModelLoadError(Exception):
    """Custom exception raised when model loading or verification fails."""
    pass

class ModelLoader:
    def __init__(self):
        self.model = None
        self.metadata = None

    def load(self, model_path: str = None, metadata_path: str = None):
        """Loads and verifies the serialized Random Forest model and metadata."""
        m_path = model_path or config.MODEL_PATH
        meta_path = metadata_path or config.METADATA_PATH

        if not os.path.exists(m_path):
            raise ModelLoadError(f"Model file not found at '{m_path}'")
        if not os.path.exists(meta_path):
            raise ModelLoadError(f"Metadata file not found at '{meta_path}'")

        try:
            self.model = joblib.load(m_path)
        except Exception as e:
            raise ModelLoadError(f"Failed to deserialize model joblib: {e}")

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        except Exception as e:
            raise ModelLoadError(f"Failed to parse metadata JSON: {e}")

        # Verification checks
        if not isinstance(self.model, RandomForestClassifier):
            raise ModelLoadError(f"Loaded model is of type {type(self.model)}, expected RandomForestClassifier")

        model_features = getattr(self.model, "n_features_in_", None)
        if model_features != 11:
            raise ModelLoadError(f"Model expects {model_features} features, expected 11")

        meta_features = self.metadata.get("feature_names", [])
        if len(meta_features) != 11:
            raise ModelLoadError(f"Metadata lists {len(meta_features)} features, expected 11")

        # Verify feature list ordering matches the fixed mapping
        expected_order = [
            "Molecular Weight", "LogP", "TPSA", "H-Bond Donors", "H-Bond Acceptors",
            "Rotatable Bonds", "Ring Count", "Aromatic Ring Count", "Heavy Atom Count",
            "Fraction CSP3", "Formal Charge"
        ]
        if meta_features != expected_order:
            raise ModelLoadError("Metadata feature names ordering is inconsistent with the production specification.")

        return self.model, self.metadata

# Global loader instance
model_loader = ModelLoader()
