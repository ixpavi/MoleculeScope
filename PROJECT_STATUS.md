# Project Status — MoleculeScope

*   **Last Updated:** 2026-08-09
*   **Current Phase:** Phase 13 — Finalize Report & Presentation Outlines (Completed)
*   **Current Phase Status:** **Completed**
*   **Completed Phases:**
    *   Phase 0: Dataset & Environment Verification
    *   Phase 1: Data Cleaning & Preprocessing Finalization
    *   Phase 2: Molecular Feature Engineering
    *   Phase 3: Dataset Splitting
    *   Phase 4: Offline Model Training
    *   Phase 5: Detailed Evaluation & Performance Plots
    *   Phase 6: Model Packaging & Serialization
    *   Phase 7: FastAPI Backend Setup
    *   Phase 8: React Frontend Core UI
    *   Phase 9: Batch Screening & Export
    *   Phase 10: Explainability (SHAP & Global Importances)
    *   Phase 11: Pytest Suite Integration (Coverage Reporting)
    *   Phase 12: Portability & Docker Deployment Config
    *   Phase 13: Finalize Report & Presentation Outlines
*   **Current Active Task:** All 13 planned phases are now complete. Remaining open items: a live `docker build`/`docker run` smoke test (Phase 12, deferred by explicit scope), and the `backend/app/dependencies.py` dead-code cleanup flagged during Phase 11.
*   **Next Planned Phase:** None currently planned — awaiting further instruction.


---

## Component Statuses

### ML Status
*   **State:** Production Model Retrained, Serialized & Verified (Phase 6 Finalized).
*   **Selected Architecture:** Random Forest Classifier trained on Descriptors Only.
*   **Evaluation Model Metrics:** Accuracy = **74.47%**, Macro F1 = **0.7212**, ROC-AUC = **0.8017**, PR-AUC = **0.8504** (evaluated on unseen scaffolds).
    *   *Note:* These metrics belong to the evaluation-split model (trained on the 6,236-sample scaffold training set and evaluated on the 1,559-sample scaffold test set). Phase 5 documents these baseline evaluation metrics for reproducibility.
*   **Deployed Production Model:** Retrained on all **7,795** cleaned molecules and saved as [production_model.joblib](file:///c:/MoleculeScope/backend/models/production_model.joblib) alongside its [production_metadata.json](file:///c:/MoleculeScope/backend/models/production_metadata.json) schema. No test metrics are claimed on this retrained production model itself.
*   **Production Preprocessing:** **Scale-free** (no scaling or column transformers needed, as Random Forest is scale-invariant).
*   **Evaluation Artifacts:**
    *   ROC Curves: `results/figures/roc_curves_random.png` and `results/figures/roc_curves_scaffold.png`
    *   Precision-Recall Curves: `results/figures/pr_curves_random.png` and `results/figures/pr_curves_scaffold.png`
    *   Confusion Matrices: `results/figures/cm_rf_descriptors_*.png` and `results/figures/cm_xgb_combined_*.png`
    *   Generalization Gap plots: `results/figures/generalization_gap_macro_f1.png` and `results/figures/generalization_gap_roc_auc.png`
    *   Feature Importance plots: `results/figures/feature_importance_rf.png` and `results/figures/feature_importance_xgb.png`
    *   Statistical Range Analysis of Errors: `results/analysis/error_analysis.md` and `results/analysis/scaffold_error_properties.csv`

### Dataset Status
*   **State:** Splits & Features Aligned (Phase 3 Finalized).
*   **Locations & Shapes:**
    *   Cleaned CSV: `backend/data/processed/b3db_cleaned.csv` (7,795 rows)
    *   Descriptors Matrix: `features/descriptors.csv` (7,795 rows, 11 features)
    *   Fingerprints Matrix: `features/fingerprints.npz` (7,795 rows, 2,048 binary features)
    *   Combined Matrix: `features/combined.npz` (7,795 rows, 2,059 features)

### Backend Status
*   **State:** FastAPI REST API Setup, Tested & Verified (Phase 7 Finalized).
*   **Details:** Exposes endpoints `GET /api/health` and `POST /api/predict` using Pydantic request/response schemas. Integrates the frozen production Random Forest model. Implements RDKit-driven canonical SMILES parsing, SVG drawings generation, and 11 descriptors extraction. Clean input validation layers reject empty/whitespace/malformed inputs before model scoring. Complete pytest suite of 11 tests passing. CORS enabled for configured Vite origin.

### Frontend Status
*   **State:** **Completed**
*   **Details:** React + Vite + TypeScript frontend core UI built, tested, and integrated. Exposes a Single Predictor screen for live SMILES inference, interactive RDKit SVG drawings, an 11 physicochemical descriptors card grid, validation errors, and a Performance tab displaying held-out scaffold metrics, majority class baselines, and model comparisons. Also exposes a Batch Screener screen (Phase 9) for CSV upload, paginated/filterable/searchable results, and CSV export. Verified with 21 Vitest unit tests (13 core UI + 8 Batch Screener) and a live browser integration run against the Uvicorn FastAPI production model service.

### Batch Screening Status (Phase 9)
*   **State:** **Completed**
*   **Backend:** `POST /api/predict/batch` accepts a `multipart/form-data` CSV upload (case-insensitive `smiles` column, 5 MB / 5,000-row limits, extra columns preserved), reuses the lifespan-loaded production model for bulk `predict`/`predict_proba` calls, and maps results back to original 1-indexed row order. Row-level errors (empty/whitespace SMILES, malformed SMILES, multi-component `.`-containing SMILES) are returned per-row rather than dropped. The existing `/api/predict` and `/api/health` endpoints are unchanged.
*   **Frontend:** New Batch Screener tab with CSV upload, sample template download, paginated (10/page) and filterable (All/BBB+/BBB-/Errors) results table, search by SMILES or extra column, and a `moleculescope_batch_results.csv` export that preserves original row order and all 11 descriptors plus extra columns. Summary statistics reflect the full uploaded batch and are unaffected by table filters.
*   **Testing:** 11 new backend pytest cases (valid batch, mixed valid/invalid, missing/case-insensitive/conflicting SMILES columns, empty CSV, blank rows, duplicates, oversized file, row-limit rejection, batch/single consistency) and 8 new frontend Vitest cases, all passing. Verified end-to-end in a live browser session against a running Uvicorn backend with a CSV containing Caffeine, Aspirin, Ibuprofen, Paracetamol, a malformed SMILES, an empty SMILES, a multi-component SMILES, and a duplicate molecule — Caffeine's batch probability matched the frozen single-prediction reference value (BBB+, 0.7898609017435456) exactly.

### Explainability Status (Phase 10)
*   **State:** **Completed**
*   **Backend:** `GET /api/explain/global` returns the frozen production model's built-in Gini `feature_importances_`, ranked descending — a direct read of the already-trained model, no recomputation. `POST /api/explain` builds a `shap.TreeExplainer` around the same frozen model (constructed once, cached in `explainability_service`) and returns per-descriptor SHAP contributions toward the BBB+ class for a single molecule, sorted by absolute magnitude. SHAP additivity (`base_value + sum(shap_values) == probability_bbb_plus`) is enforced in tests. The existing `/api/predict`, `/api/predict/batch`, and `/api/health` endpoints are unmodified.
*   **Frontend:** `GlobalImportanceChart` added to the Performance tab (bar chart of the 11 descriptors ranked by importance). `ShapExplanationCard` added to the Predictor tab, rendered automatically after each successful prediction, showing a diverging bar per descriptor (positive = pushes toward BBB+, negative = pushes toward BBB-).
*   **Testing:** 6 new backend pytest cases (global importance shape/ordering/determinism, local SHAP additivity/determinism, empty/malformed SMILES validation) and 2 new frontend Vitest cases, all passing. Verified end-to-end in a live browser session against a running Uvicorn backend: Caffeine's SHAP contributions and the global importance ranking (TPSA highest at 28.5%) matched direct API responses exactly.

### Test Coverage Status (Phase 11)
*   **State:** **Completed**
*   **Backend:** `pytest-cov` added (`backend/requirements.txt`). Coverage scoped to `backend/app` (excludes offline Phase 0-6 training/analysis scripts under `backend/src`, which are validated separately by their own Phase 0-6 artifacts). Overall: **91% statement coverage** (417 statements, 39 missed) across 33 passing tests. `backend/app/dependencies.py` (0%) was identified as genuinely unused dead code and flagged separately rather than fixed inline — nothing imports its `get_model`/`get_metadata` helpers. Remaining gaps are narrow (the `sys.exit(1)` fail-fast branch in `main.py`'s lifespan handler, and a few defensive `except` branches in `model_loader.py`/`molecule.py`) and low-value to chase further. HTML report: `backend/tests/coverage_html/index.html`.
*   **Frontend:** `@vitest/coverage-v8` added; `npm run test:coverage` runs the 23-test Vitest suite with coverage. Overall: **67.4% statement coverage** across `src/components` and `App.tsx`. Coverage is uneven by design — components exercised directly by tests (`PredictorPage`, `GlobalImportanceChart`, `ShapExplanationCard`, `SmilesInput`, `DescriptorTable`) sit at 90-100%, while `AppShell.tsx` (mostly static nav/branding markup) and `PredictionResult.tsx`'s copy-to-clipboard handlers are lower since those interactions aren't yet asserted. HTML report: `frontend/coverage/index.html`.

### Deployment Status (Phase 12)
*   **State:** **Dockerfile authored; live build not yet run.**
*   **Details:** Root [Dockerfile](file:///c:/MoleculeScope/Dockerfile) implements the multi-stage build documented in `docs/DEPLOYMENT.md`: a `node:22-alpine` stage builds the frontend (`npm ci && npm run build`), and a `python:3.13-slim` stage installs backend dependencies (plus `libxrender1`/`libxext6` for headless RDKit SVG rendering and `libgomp1` for scikit-learn), copies the frozen `backend/models/` artifacts unmodified, and copies the built frontend into `frontend/dist`. `backend/app/main.py` now conditionally mounts `frontend/dist` as static files at `/` (via a new `config.FRONTEND_DIST_PATH` setting, default `frontend/dist`) — only when that directory exists, and registered after all `/api/*` routers so API routes always take precedence. Local development is unaffected either way.
*   **Verification performed:** Ran a real `npm run build` to produce `frontend/dist`, then started `uvicorn` locally with that directory present — confirmed `GET /api/health` still resolves correctly, `GET /` serves the built `index.html`, and static assets (e.g. `favicon.svg`) resolve with `200`. Re-ran the full 33-test backend pytest suite with the static mount active — all pass, confirming the mount doesn't shadow any `/api/*` route.
*   **Not verified:** An actual `docker build -t moleculescope .` / `docker run` was **not** executed in this environment (per explicit scope: write the config, don't build). Deployment platform choice (Hugging Face Spaces / Render / Vercel+Render) remains unchosen to preserve portability, per `docs/DEPLOYMENT.md` §2.

---

## Important Decisions
1.  **Selection of Descriptors-only Random Forest:** Replaced XGBoost-Combined as the production recommendation. Even though XGBoost-Combined achieved slightly higher ranking discrimination (ROC-AUC 0.8138 vs. 0.8017), Random Forest on Descriptors generalizes significantly better (Macro F1 of 0.7212 vs. 0.6838), features lower memory/latency (11 inputs vs. 2,059), and permits direct physical explainability.
2.  **Fingerprint Generalization Defect:** Documented that ECFP4 fingerprints overfit structural motifs and collapse on unseen scaffolds (Random Forest Macro F1 drop of **-0.2626** from 0.8172 to 0.5546). Descriptors are robust to structural distributions (drop of only **-0.1392**).
3.  **Active Transporter Limitation:** Documented that passive descriptors-only classifiers misclassify carrier-mediated penetrants as BBB- (False Negatives, mean TPSA = 97.67 Å²), and misclassify polar-blocked compounds as BBB+ (False Positives, mean TPSA = 61.13 Å²).

---

## Known Issues
*   **Tiotidine Structure Error:** Row 7737 in the B3DB classification dataset contains a duplicate of mepenzolate bromide's structure instead of tiotidine. Excluded in Phase 1.

---

## Current TODOs
1.  `[x]` Obtain approval for Phase 5 corrected evaluation results and the Project Status file.
2.  `[x]` Complete Phase 6: Retrained the selected Random Forest architecture (with 11 descriptors, scale-free) on the full cleaned dataset of 7,795 molecules, packaged as `production_model.joblib` to `backend/models/`, and successfully passed all automated verification checks.
    *   *Workflow:* Model selection $\rightarrow$ Preserve scaffold evaluation results $\rightarrow$ Retrain on all 7,795 molecules $\rightarrow$ Save as the production model (Completed).
3.  `[x]` Complete Phase 7: Set up FastAPI REST API endpoints to load the serialized production pipeline and serve single molecule predictions. Coded a robust automated pytest suite (11 tests passing) and verified endpoints manually.
4.  `[x]` Complete Phase 8: Build the Vite + React client shell with single molecular property predicting and model metrics comparison visualizations (Completed).
5.  `[x]` Complete Phase 9: Implemented CSV batch uploader (`POST /api/predict/batch`), paginated/filterable/searchable Batch Screener results table, and CSV export functionality. 11 new backend + 8 new frontend tests passing; verified end-to-end against a live FastAPI + Vite integration.
6.  `[x]` Complete Phase 10: Implemented `GET /api/explain/global` (frozen model's Gini importances) and `POST /api/explain` (cached SHAP TreeExplainer, per-molecule local contributions), plus the corresponding `GlobalImportanceChart` and `ShapExplanationCard` frontend components. 6 new backend + 2 new frontend tests passing; verified end-to-end against a live FastAPI + Vite integration.
7.  `[x]` Complete Phase 11: Added `pytest-cov`/`@vitest/coverage-v8` coverage reporting to both suites, added 5 targeted backend tests for previously-uncovered error branches (500 handling, unloaded-model health check, blank-CSV edge cases), and raised backend coverage from 88% to 91% (33 tests). Documented coverage numbers and flagged unused `backend/app/dependencies.py` for separate cleanup.
8.  `[x]` Complete Phase 12: Authored the multi-stage `Dockerfile` and `.dockerignore`, added an opt-in static-file mount to `backend/app/main.py` (new `FRONTEND_DIST_PATH` config), and verified the mount mechanism locally with a real frontend build + uvicorn run (33/33 backend tests still passing). Live `docker build`/`run` intentionally deferred per scope.
9.  `[x]` Complete Phase 13: Filled in the `docs/REPORT_OUTLINE.md` §11 Results & Discussion placeholder with the full 20-run model comparison table, generalization-gap analysis, error analysis, and Phase 10 explainability findings; updated §12/§13 to describe the Batch Screener and Explainability Hub and the current (unbuilt) Docker status. Filled in `docs/PRESENTATION_OUTLINE.md` slides 10-12 with the same results, and updated slides 13-14. Fixed a factual error in `docs/VIVA_QUESTIONS.md` Q15 (claimed the production `.joblib` bundles a `StandardScaler`, contradicting the documented scale-free Random Forest production package) and added Q16/Q17 covering batch screening and the Docker static-mount design.
