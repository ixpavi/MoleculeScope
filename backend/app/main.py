import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config
from .services.model_loader import model_loader, ModelLoadError
from .routes import health, predict, batch, explain, molecules

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle: Load the production model and metadata
    try:
        model_loader.load()
    except ModelLoadError as e:
        # Write error directly to stderr and exit with non-zero code to fail-fast
        sys.stderr.write(f"CRITICAL STARTUP ERROR: Failed to load production package. {str(e)}\n")
        sys.stderr.flush()
        sys.exit(1)
    yield
    # Shutdown lifecycle: Cleanup if needed
    pass

app = FastAPI(
    title="MoleculeScope REST API",
    description="REST API service for blood-brain barrier permeability prediction using a frozen RandomForestClassifier.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS origins
# ALLOWED_ORIGINS defaults to http://localhost:5173 for local development.
# Unrestricted wildcards (*) are disabled in production configurations.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers namespaced under config.API_PREFIX (/api)
app.include_router(health.router, prefix=config.API_PREFIX, tags=["Health"])
app.include_router(predict.router, prefix=config.API_PREFIX, tags=["Prediction"])
app.include_router(batch.router, prefix=config.API_PREFIX, tags=["Prediction"])
app.include_router(explain.router, prefix=config.API_PREFIX, tags=["Explainability"])
app.include_router(molecules.router, prefix=config.API_PREFIX, tags=["Molecules"])

# Phase 5 evaluation figures (ROC/PR curves, confusion matrices), served read-only for the
# Performance tab. Registered before the catch-all frontend mount below so it takes
# precedence for this path prefix; skipped if the directory is absent.
if os.path.isdir(config.RESULTS_FIGURES_PATH):
    app.mount("/static/figures", StaticFiles(directory=config.RESULTS_FIGURES_PATH), name="figures")

# Optional single-container deployment mode (Phase 12): if a built frontend bundle is
# present at FRONTEND_DIST_PATH (e.g. baked into the Docker image), serve it as static
# files at the root path. Local development (Vite dev server on :5173) is unaffected
# when this directory is absent, since the mount is skipped entirely. Registered last so
# it never shadows the /api/* routers above.
if os.path.isdir(config.FRONTEND_DIST_PATH):
    app.mount("/", StaticFiles(directory=config.FRONTEND_DIST_PATH, html=True), name="frontend")
