import shap
import numpy as np
from .model_loader import model_loader


class ExplainabilityService:
    """Lazily builds a SHAP TreeExplainer around the frozen production model and
    caches it for reuse across requests. No retraining or model mutation occurs here."""

    def __init__(self):
        self._explainer = None

    def _get_explainer(self):
        if self._explainer is None:
            self._explainer = shap.TreeExplainer(model_loader.model)
        return self._explainer

    def get_global_importance(self) -> list[dict]:
        """Returns the frozen model's built-in Gini feature importances, sorted descending."""
        model = model_loader.model
        feature_names = model_loader.metadata["feature_names"]
        importances = model.feature_importances_

        ranked = sorted(
            zip(feature_names, importances),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [{"descriptor": name, "importance": float(value)} for name, value in ranked]

    def get_local_explanation(self, feature_vector: list[float]) -> dict:
        """Computes per-descriptor SHAP contributions toward the BBB+ (class 1) prediction
        for a single molecule's feature vector, in the model's fixed feature order."""
        feature_names = model_loader.metadata["feature_names"]
        explainer = self._get_explainer()

        X = np.array([feature_vector])
        shap_values = explainer.shap_values(X)

        # shap>=0.42 TreeExplainer returns shape (n_samples, n_features, n_classes) for
        # binary RandomForestClassifier. Class index 1 corresponds to BBB+ (target_mapping).
        class_idx = 1
        contributions = shap_values[0, :, class_idx]
        base_value = float(np.array(explainer.expected_value)[class_idx])

        rows = [
            {
                "descriptor": name,
                "descriptor_value": float(feature_vector[i]),
                "shap_value": float(contributions[i]),
            }
            for i, name in enumerate(feature_names)
        ]
        rows.sort(key=lambda row: abs(row["shap_value"]), reverse=True)

        return {
            "base_value": base_value,
            "contributions": rows,
        }


explainability_service = ExplainabilityService()
