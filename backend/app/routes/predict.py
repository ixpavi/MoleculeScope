from fastapi import APIRouter, HTTPException
from ..schemas.prediction import SMILESRequest, PredictionResponse
from ..services.predictor import predict_smiles
from ..services.molecule import validate_and_parse_smiles

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse, summary="Predict blood-brain barrier permeability")
def predict(request: SMILESRequest):
    """
    Computes 11 physicochemical descriptors for the input SMILES string using RDKit,
    generates 2D coordinates to render an SVG representation, and scores the
    frozen production Random Forest classifier to predict permeability.
    """
    smiles = request.smiles
    
    # 1. Validation for empty / whitespace inputs
    if not smiles or not smiles.strip():
        raise HTTPException(
            status_code=400,
            detail="SMILES input cannot be empty or whitespace-only."
        )
        
    # 2. Validation for malformed SMILES strings
    is_valid, mol_or_err = validate_and_parse_smiles(smiles)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=mol_or_err
        )
        
    # 3. Model inference pipeline execution
    try:
        results = predict_smiles(smiles)
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # Suppress internal Python tracebacks for safety, return a clean error
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during model inference: {str(e)}"
        )
