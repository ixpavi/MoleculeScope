# Deployment Strategy — MoleculeScope

This document outlines the deployment configuration designed to host the full-stack MoleculeScope application on free hosting platforms.

---

## 1. Portable Deployment Architecture

The application is containerized using a multi-stage Docker configuration defined in the root [Dockerfile](file:///c:/MoleculeScope/Dockerfile). This ensures that the frontend and backend run as a single self-contained unit, removing cross-origin resource sharing (CORS) concerns and allowing deployment to free container services.

*   **Status (Phase 12):** The `Dockerfile` and `.dockerignore` have been authored and the underlying FastAPI static-mount behavior has been verified locally (`uvicorn` + a `frontend/dist` build served together — see `CHANGELOG.md` Phase 12 entry). A live `docker build`/`docker run` has **not** been executed in this environment; it should be run and smoke-tested (health check + a real prediction through the served UI) before relying on this image for actual deployment.

### Multi-Stage Dockerfile
*   **Stage 1 (Frontend Builder — `frontend-builder`):**
    *   Base Image: `node:22-alpine`
    *   Action: Copies `frontend/package.json` + `package-lock.json`, runs `npm ci`, copies the rest of `frontend/`, and builds production assets (`npm run build`). Outputs static HTML/JS/CSS to `frontend/dist/`.
*   **Stage 2 (Backend Runner — `backend`):**
    *   Base Image: `python:3.13-slim`
    *   Action: Installs `libxrender1`/`libxext6` (required by RDKit's headless `rdMolDraw2D` SVG rendering) and `libgomp1` (required by scikit-learn's OpenMP-parallelized Random Forest inference), then installs Python packages from `backend/requirements.txt`. Copies `backend/app`, `backend/src`, and the frozen `backend/models` artifacts (unmodified — no retraining occurs during the build). Copies the compiled frontend from Stage 1 into `frontend/dist`.
    *   Serving: `backend/app/main.py` conditionally mounts `frontend/dist` as static files at the root path (`/`) via `FastAPI.mount`, only when that directory exists — so local development (Vite dev server on `:5173`, no built `dist/`) is unaffected. All API calls remain at `/api/*` (the existing `config.API_PREFIX`, unchanged from Phases 7-10), registered *before* the static mount so they always take precedence.
    *   *Result:* A single container running on port `8000` that serves both the UI and backend logic.

---

## 2. Potential Free Hosting Providers

To keep hosting free, the application is designed to be deployed to one of the following services:

### A. Hugging Face Spaces (Docker Space)
*   **Cost:** 100% Free (under CPU Basic hardware).
*   **Setup:**
    *   Create a Hugging Face Space.
    *   Select the SDK as **Docker**.
    *   Push the monorepo. Hugging Face will build the Dockerfile and expose port 7860 automatically.
*   **Limitations:** The Space goes to sleep after 48-72 hours of inactivity. The UI will show a wake-up indicator during cold starts.

### B. Render (Web Service)
*   **Cost:** Free tier available for web services.
*   **Setup:**
    *   Connect the GitHub repository to Render.
    *   Select environment as **Docker**.
*   **Limitations:** Render free tier spins down containers after 15 minutes of inactivity. Cold starts can take up to 50 seconds to spin up.

### C. Vercel (Frontend) + Render (Backend)
*   **Cost:** Free.
*   **Setup:**
    *   Host the React frontend statically on Vercel.
    *   Host the FastAPI backend on Render or Hugging Face.
*   **Limitations:** Requires CORS middleware enabled in FastAPI to accept requests from the Vercel domain.

---

## 3. Deployed Production Model Assets (Phase 6 Completed)

During Phase 6, the production model was successfully trained on all **7,795** cleaned molecules and serialized into the backend directory. The deployment package includes:
*   **Model Binary:** [production_model.joblib](file:///c:/MoleculeScope/backend/models/production_model.joblib) (Trained Random Forest Classifier)
*   **Metadata Specification:** [production_metadata.json](file:///c:/MoleculeScope/backend/models/production_metadata.json) (Specifies exact descriptor lists, feature ordering, and training environment packages)

### Deployment Characteristics:
*   **Scale-Free Integration:** The backend serves the model directly on raw dynamically calculated descriptors without requiring scaler conversions.
*   **Low Memory Overhead:** Because the model runs strictly on 11 physical descriptors and does not load Morgan fingerprints, the FastAPI server keeps memory footprints low, fitting easily inside Hugging Face CPU Basic or Render Free tiers.
*   **Generalization Benchmark Reference:** The model is described as: "Retrained on the complete cleaned dataset after model selection, using the architecture validated through the Phase 5 scaffold-split evaluation." No test performance is claimed on this retrained production model itself. The scaffold-split evaluation metrics (Accuracy = 74.47%, Macro F1 = 0.7212, ROC-AUC = 0.8017) are preserved strictly as the reference baseline.

---

## 4. Backend Environment Variables & CORS Config (Phase 7 Completed)

The FastAPI server reads configuration from the environment with safe local fallbacks:

*   **`MODEL_PATH`**: Path to the serialized production model (default: `backend/models/production_model.joblib`).
*   **`METADATA_PATH`**: Path to the serialized metadata JSON (default: `backend/models/production_metadata.json`).
*   **`ALLOWED_ORIGINS`**: Comma-separated list of domains allowed to request resources. For development, this defaults to `http://localhost:5173` (Vite dev server). Wildcards (`*`) are disabled in production configurations to protect prediction endpoints. In the single-container Docker image the `Dockerfile` sets this to an empty string (no CORS origins needed, since the frontend and API are served from the same origin).
*   **`FRONTEND_DIST_PATH`** *(Phase 12)*: Path to a built frontend bundle to serve as static files at `/`. Defaults to `frontend/dist`. If the directory doesn't exist (the normal case in local development), the static mount is skipped entirely and only the `/api/*` routes are served.

### Fail-Fast Behavior
If the model file is missing or verification fails during container boot, the server logs a critical message to `stderr` and terminates immediately with exit code `1`. This prevents container instances from running in a semi-functional state.

---

## 5. Batch Screening Endpoint (Phase 9 Completed)

`POST /api/predict/batch` was added alongside the existing `/api/predict` endpoint and shares the same lifespan-loaded production model — no additional model instance is created and no extra memory overhead is introduced at container boot. CSV uploads are capped at 5 MB / 5,000 rows and are parsed and scored in-memory per request with no persistence to disk, keeping the deployment footprint identical to Phase 7/8.

---

## 6. Building & Running the Container (Phase 12)

```bash
# From the repository root:
docker build -t moleculescope .
docker run -p 8000:8000 moleculescope
```

Then open `http://localhost:8000` for the UI, or `http://localhost:8000/api/health` for the API health check. No `docker-compose` file is provided since the entire application runs as one container/one process.

**Not yet done in this environment:** an actual `docker build` + `docker run` + browser smoke test of the built image. The `Dockerfile`'s correctness was instead verified indirectly — the same static-mount code path (`backend/app/main.py` conditionally serving `frontend/dist`) was exercised locally with a real `npm run build` output and a real `uvicorn` process, confirming `/api/health` and the served UI both work together (see `CHANGELOG.md` Phase 12 entry for exact commands/output). Before relying on this image for a real deployment, run the build above at least once and verify a prediction end-to-end through the served UI.


