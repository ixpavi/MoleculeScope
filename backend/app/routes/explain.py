from fastapi import APIRouter, HTTPException
from ..schemas.prediction import SMILESRequest, GlobalImportanceResponse, ExplanationResponse
from ..services.molecule import validate_and_parse_smiles, process_molecule
from ..services.explainability import explainability_service
from ..services.model_loader import model_loader

router = APIRouter()


@router.get(
    "/explain/global",
    response_model=GlobalImportanceResponse,
    summary="Get global feature importances for the production model"
)
def explain_global():
    """
    Returns the frozen production Random Forest's built-in Gini feature importances
    for all 11 physicochemical descriptors, ranked descending. No retraining occurs.
    """
    importances = explainability_service.get_global_importance()
    return {"feature_importances": importances}


@router.post(
    "/explain",
    response_model=ExplanationResponse,
    summary="Get a local SHAP explanation for a single SMILES prediction"
)
def explain_local(request: SMILESRequest):
    """
    Computes per-descriptor SHAP contributions toward the BBB+ prediction for a single
    molecule, using the same frozen production model and descriptor pipeline as /predict.
    """
    smiles = request.smiles

    if not smiles or not smiles.strip():
        raise HTTPException(
            status_code=400,
            detail="SMILES input cannot be empty or whitespace-only."
        )

    is_valid, mol_or_err = validate_and_parse_smiles(smiles)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=mol_or_err
        )

    try:
        mol_data = process_molecule(smiles)
        feature_names = model_loader.metadata["feature_names"]
        feature_vector = [mol_data["descriptors"][name] for name in feature_names]

        model = model_loader.model
        X = [feature_vector]
        pred_class_idx = int(model.predict(X)[0])
        prediction_label = "BBB+" if pred_class_idx == 1 else "BBB-"
        prob_bbb_plus = float(model.predict_proba(X)[0][1])

        explanation = explainability_service.get_local_explanation(feature_vector)

        return {
            "canonical_smiles": mol_data["canonical_smiles"],
            "prediction": prediction_label,
            "probability_bbb_plus": prob_bbb_plus,
            "base_value": explanation["base_value"],
            "contributions": explanation["contributions"],
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during SHAP explanation: {str(e)}"
        )
