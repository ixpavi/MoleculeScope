# MoleculeScope — Multi-stage Docker build (Phase 12)
#
# Produces a single container that serves both the built React frontend and the
# FastAPI backend on one port. See docs/DEPLOYMENT.md for hosting options.
#
# Build:  docker build -t moleculescope .
# Run:    docker run -p 8000:8000 moleculescope

# ---- Stage 1: Frontend builder ----
FROM node:22-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Backend runner ----
FROM python:3.13-slim AS backend

WORKDIR /app

# libxrender1/libxext6 are required by RDKit's headless 2D drawing (rdMolDraw2D) in a
# minimal Debian slim image; libgomp1 is required by scikit-learn's OpenMP-parallelized
# RandomForestClassifier inference.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/app ./backend/app
COPY backend/src ./backend/src
COPY backend/models ./backend/models

# Runtime data dependencies beyond the frozen model itself:
#   - backend/data/processed/b3db_cleaned.csv: compound name search (GET /api/molecules/search)
#     and applicability domain neighbor identities (part of POST /api/predict).
#   - features/fingerprints.npz: applicability domain Tanimoto similarity search.
#   - features/descriptors.csv: real training-distribution percentile rank per descriptor.
#   - results/figures: Phase 5 evaluation plots served read-only for the Performance tab.
# None of these are written to at runtime, and none require retraining to reproduce —
# they are copied as-is from this repo's existing artifacts.
COPY backend/data/processed ./backend/data/processed
COPY features/fingerprints.npz ./features/fingerprints.npz
COPY features/descriptors.csv ./features/descriptors.csv
COPY results/figures ./results/figures

# Built frontend bundle, served by FastAPI's static mount (see backend/app/main.py and
# FRONTEND_DIST_PATH in backend/app/config.py) when this directory is present.
COPY --from=frontend-builder /frontend/dist ./frontend/dist

ENV ALLOWED_ORIGINS=""
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
