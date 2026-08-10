import os

# Configuration variables for the FastAPI backend
MODEL_PATH = os.getenv("MODEL_PATH", "backend/models/production_model.joblib")
METADATA_PATH = os.getenv("METADATA_PATH", "backend/models/production_metadata.json")

# Cleaned B3DB dataset used to power compound name search (GET /api/molecules/search) and
# applicability domain nearest-neighbor lookup (part of POST /api/predict). Both are
# convenience/interpretability features, not the prediction pipeline itself: if this file
# is unavailable, they degrade to empty results rather than failing the app.
CLEANED_DATASET_PATH = os.getenv("CLEANED_DATASET_PATH", "backend/data/processed/b3db_cleaned.csv")

# Precomputed Morgan fingerprint matrix (7,795 x 2,048, row-aligned with
# CLEANED_DATASET_PATH) used for applicability domain nearest-neighbor similarity search.
FINGERPRINTS_PATH = os.getenv("FINGERPRINTS_PATH", "features/fingerprints.npz")

# Phase 5 evaluation figures (ROC/PR curves, confusion matrices, etc.), served as static
# files at /static/figures/<filename>.png for the Performance tab. Read-only reference
# artifacts; never written to by the running app.
RESULTS_FIGURES_PATH = os.getenv("RESULTS_FIGURES_PATH", "results/figures")

# Real 7,795-molecule training descriptor matrix, used to compute each predicted
# molecule's percentile rank within the actual training distribution (not simulated).
DESCRIPTOR_STATS_PATH = os.getenv("DESCRIPTOR_STATS_PATH", "features/descriptors.csv")

# Optional built frontend bundle for single-container deployment (Phase 12).
# Absent in local development (Vite dev server serves the frontend separately on :5173);
# present inside the Docker image, where the multi-stage build copies frontend/dist here.
FRONTEND_DIST_PATH = os.getenv("FRONTEND_DIST_PATH", "frontend/dist")

# CORS Configuration
# Vite standard dev port is 5173. Comma-separated list for multiple origins.
ALLOWED_ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_RAW.split(",") if origin.strip()]

# API namespaces
API_PREFIX = "/api"
