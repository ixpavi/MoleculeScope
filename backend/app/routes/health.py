from fastapi import APIRouter
from ..schemas.prediction import HealthResponse
from ..services.model_loader import model_loader

router = APIRouter()

@router.get("/health", response_model=HealthResponse, summary="Perform server health check")
def health_check():
    """
    Checks the status of the server and confirms if the frozen production model
    and metadata are loaded successfully.
    """
    model_loaded = (model_loader.model is not None) and (model_loader.metadata is not None)
    
    if model_loaded:
        model_type = model_loader.metadata.get("model_type", "RandomForestClassifier")
        model_version = model_loader.metadata.get("model_version", "1.0.0")
    else:
        model_type = "None"
        model_version = "None"
        
    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "model_type": model_type,
        "model_version": model_version
    }
