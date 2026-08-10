# REST API Specification — MoleculeScope

This document outlines the REST API exposed by the FastAPI backend to interface with the MoleculeScope prediction pipeline. Example payloads do not contain hardcoded or fabricated values.

---

## 1. Global API Prefix
All endpoints are namespaced under the root prefix: `/api`

---

## 2. API Schemas & Request/Response Contracts

### A. Health Check
*   **Path:** `GET /api/health`
*   **Response Schema (`HealthResponse`):**
    ```json
    {
      "status": "ok",
      "model_loaded": true,
      "model_type": "RandomForestClassifier",
      "model_version": "1.0.0"
    }
    ```

### B. Single Prediction
*   **Path:** `POST /api/predict`
*   **Request Schema (`SMILESRequest`):**
    ```json
    {
      "smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"
    }
    ```
*   **Response Schema (`PredictionResponse`):**
    ```json
    {
      "prediction": "BBB+",
      "probability_bbb_plus": 0.7898609017435456,
      "probability_bbb_minus": 0.2101390982564544,
      "canonical_smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O",
      "molecular_formula": "C8H10N4O2",
      "svg": "<svg>...</svg>",
      "descriptors": {
        "Molecular Weight": 194.19399999999996,
        "LogP": -1.029300000000001,
        "TPSA": 61.82,
        "H-Bond Donors": 0.0,
        "H-Bond Acceptors": 3.0,
        "Rotatable Bonds": 0.0,
        "Ring Count": 2.0,
        "Aromatic Ring Count": 2.0,
        "Heavy Atom Count": 14.0,
        "Fraction CSP3": 0.375,
        "Formal Charge": 0.0
      },
      "applicability_domain": {
        "max_similarity": 1.0,
        "nearest_neighbors": [
          { "name": "58-08-2", "smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O", "bbb_label": "BBB+", "similarity": 1.0 },
          { "name": "dimethazan", "smiles": "...", "bbb_label": "BBB+", "similarity": 0.568 }
        ]
      },
      "uncertainty": {
        "tree_probability_std": 0.2731,
        "tree_probability_iqr_low": 0.6988,
        "tree_probability_iqr_high": 1.0
      }
    }
    ```
    *   **`applicability_domain`:** Tanimoto similarity (Morgan fingerprints, radius=2, nBits=2048 — same settings as training) between the query and the 5 most similar molecules in the 7,795-molecule training set, computed via `backend/app/services/applicability_domain.py`. The frozen model has no built-in notion of "out of distribution"; this is a post-hoc signal for whether a prediction is interpolating within familiar chemical space or extrapolating. `max_similarity` is `null` if the fingerprint dataset is unavailable — this never blocks a prediction from returning.
    *   **`uncertainty`:** Spread of the 250 individual Random Forest tree votes for the BBB+ class. Informational only — never presented as a calibrated confidence interval, consistent with this project's rule that model output is called "predicted probability," not "confidence."
    ```

### C. Batch Prediction
*   **Path:** `POST /api/predict/batch`
*   **Content-Type:** `multipart/form-data`
*   **Request:** `file` — a CSV file containing a case-insensitive `smiles` column (extra columns are preserved and echoed back per row).
*   **Constraints:** Max file size 5 MB. Max 5,000 data rows (blank lines are skipped and don't count). Exactly one `smiles`-named column (case-insensitive) is required; more than one is rejected as a conflict.
*   **Response Schema (`BatchPredictionResponse`):**
    ```json
    {
      "summary": {
        "filename": "library.csv",
        "total_rows": 4,
        "processed_rows": 3,
        "failed_rows": 1,
        "bbb_plus_count": 3,
        "bbb_minus_count": 0
      },
      "results": [
        {
          "row_index": 1,
          "input_smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O",
          "status": "success",
          "error": null,
          "prediction": "BBB+",
          "probability_bbb_plus": 0.7898609017435456,
          "probability_bbb_minus": 0.2101390982564544,
          "canonical_smiles": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
          "molecular_formula": "C8H10N4O2",
          "descriptors": { "...": "11 descriptors, same shape as single prediction" },
          "extra_columns": { "Compound_ID": "Caffeine" }
        }
      ]
    }
    ```
*   **Row-level errors:** Empty/whitespace SMILES, malformed SMILES, and multi-component SMILES (containing `.`) each produce a row with `status: "error"`, a populated `error` message, and `null` for all prediction/descriptor fields — the row is never silently dropped, and original 1-indexed row order is always preserved.
*   **No SVG in batch responses:** Unlike `/api/predict`, batch rows omit the `svg` field to keep payloads compact for up to 5,000 rows; SVG rendering remains exclusive to the single-molecule endpoint.
*   **File/CSV-level errors (`400 Bad Request`):** missing `smiles` column, conflicting duplicate `smiles` columns, empty CSV, file over 5 MB, more than 5,000 data rows, or an unparseable/malformed CSV structure.

### D. Global Feature Importance
*   **Path:** `GET /api/explain/global`
*   **Response Schema (`GlobalImportanceResponse`):** The frozen production model's built-in Gini-based `feature_importances_`, ranked descending. No SHAP computation, retraining, or background dataset is involved — this is a direct read of the already-trained model attribute.
    ```json
    {
      "feature_importances": [
        { "descriptor": "TPSA", "importance": 0.2854016484594919 },
        { "descriptor": "LogP", "importance": 0.11621278889654618 }
      ]
    }
    ```

### E. Local SHAP Explanation
*   **Path:** `POST /api/explain`
*   **Request Schema:** Same as `SMILESRequest` (`{"smiles": "..."}`).
*   **Response Schema (`ExplanationResponse`):** Per-descriptor SHAP contributions toward the BBB+ class for this specific molecule, computed via a cached `shap.TreeExplainer` around the frozen production model. Sorted by absolute contribution magnitude, descending.
    ```json
    {
      "canonical_smiles": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
      "prediction": "BBB+",
      "probability_bbb_plus": 0.7898609017435456,
      "base_value": 0.5004120590121872,
      "contributions": [
        { "descriptor": "H-Bond Donors", "descriptor_value": 0.0, "shap_value": 0.08004450910614255 },
        { "descriptor": "TPSA", "descriptor_value": 61.82, "shap_value": 0.06939547137823321 }
      ]
    }
    ```
*   **Additivity invariant:** `base_value + sum(contributions[*].shap_value) == probability_bbb_plus` (within floating-point tolerance) — verified in the automated test suite.
*   **Validation:** Empty/whitespace and malformed SMILES return `400 Bad Request` with the same messages as `/api/predict`.
*   **Existing endpoints unchanged:** `/api/predict`, `/api/predict/batch`, and `/api/health` are unmodified by Phase 10.

### F. Compound Name Search
*   **Path:** `GET /api/molecules/search?q=<query>&limit=<n>`
*   Searches the `compound_name` column of the 7,795-molecule cleaned B3DB dataset (prefix matches ranked before substring matches), returning `{"results": [{"name", "smiles"}, ...]}`. Names are taken as-is from the source dataset and are **not** independently verified against their SMILES — some names in B3DB map to multiple, occasionally conflicting structures (a known data-quality characteristic of aggregating ~50 source studies), so every distinct match is returned rather than silently picking one. `q` is required (`422` if missing); `limit` defaults to 20, max 50. Returns an empty list (not an error) for unmatched queries or if the source dataset is unavailable.

### G. Evaluation Figures (static, outside `/api` prefix)
*   **Path:** `GET /static/figures/<filename>.png`
*   Serves the Phase 5 evaluation plots (ROC/PR curves, confusion matrices, generalization gap charts) in `results/figures/` as static files, for display in the frontend Performance tab. Read-only; not namespaced under `/api` since it isn't a JSON API endpoint. The mount is skipped entirely if `results/figures` doesn't exist on disk (see `RESULTS_FIGURES_PATH` in `backend/app/config.py`), matching the same conditional pattern as the Phase 12 frontend static mount.

---

## 3. Input Validation & Error Payload Structure

The API enforces strict input validation. If validation fails, it returns standard HTTP error codes with user-friendly descriptions (Python tracebacks are hidden for security):

### A. Empty or Whitespace-Only SMILES
*   **Request:** `{"smiles": "   "}` or `{"smiles": ""}`
*   **Response Code:** `400 Bad Request`
*   **Payload:**
    ```json
    {
      "detail": "SMILES input cannot be empty or whitespace-only."
    }
    ```

### B. Malformed SMILES
*   **Request:** `{"smiles": "NOT_A_SMILES"}`
*   **Response Code:** `400 Bad Request`
*   **Payload:**
    ```json
    {
      "detail": "Invalid or malformed SMILES string: 'NOT_A_SMILES'."
    }
    ```

### C. Missing Field
*   **Request:** `{}`
*   **Response Code:** `422 Unprocessable Entity`
*   **Payload:** Standard Pydantic field validation error list.

---

## 4. Design Decisions & Chemistry Representation

*   **RDKit Canonicalization:** The response returns the standardized `canonical_smiles` generated by RDKit to ensure equivalent inputs (e.g. `CCO` vs `OCC`) map to the same chemical representation.
*   **Molecular Formula:** Computed dynamically using RDKit's `rdMolDescriptors.CalcMolFormula(mol)`.
*   **Compact Molecule Visualization:** To support frontend rendering, the API generates a compact 2D molecular drawing represented as an SVG string (`svg` field, sized `300x300`, transparent background). This avoids sending heavy binary image files or introducing external image rendering dependencies.
*   **Model Lifecycle:** The frozen model (`production_model.joblib`) is loaded once during the lifespan startup event and cached in memory. In case of loading failure (e.g., missing model or metadata), the server crashes immediately to prevent running in an unserviceable state.
