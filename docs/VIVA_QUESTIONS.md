# Viva Voce Questions & Answers — MoleculeScope

This document prepares students for oral defense (viva) examinations regarding the **MoleculeScope** machine learning and cheminformatics project.

---

### Q1: What is the Blood-Brain Barrier (BBB) and why does predicting permeability matter?
*   **Answer:** The BBB is a highly selective semipermeable border of endothelial cells that prevents solutes in circulating blood from non-selectively crossing into the central nervous system. In drug discovery, central nervous system (CNS) active drugs must cross the BBB (BBB+), whereas non-CNS active drugs (like antihistamines) should not cross it to avoid side effects (BBB-). Early computational prediction screens out poor candidates before expensive wet-lab assays.

### Q2: What is the difference between BBBP and B3DB? Why did you use B3DB?
*   **Answer:** BBBP (Blood-Brain Barrier Penetration) is a commonly used dataset from MoleculeNet containing ~2,000 compounds. B3DB is the Blood-Brain Barrier Database, which is much larger (~7,800 compounds) and compiles data from 50 separate published resources. It includes categorical labels, experimental consistency grouping (A, B, C), and numerical logBB values for a subset, making it a more robust and comprehensive benchmark.

### Q3: What are Bemis-Murcko scaffolds, and how does scaffold splitting differ from random splitting?
*   **Answer:** A Bemis-Murcko scaffold is the core framework of a molecule, obtained by removing all side chains (substituents) and keeping only the ring systems and linker chains.
    *   **Random Splitting:** Allocates molecules randomly. Molecules with very similar core structures (scaffolds) will be present in both the training and testing sets, leading to data leakage and overly optimistic test performance.
    *   **Scaffold Splitting:** Groups molecules by their Bemis-Murcko scaffold and allocates entire scaffold groups to either train or test. This guarantees that the test set only contains structurally novel chemotypes, testing the model's genuine generalization capacity.

### Q4: Why didn't you enforce the same class distribution in the scaffold split as the random split?
*   **Answer:** In real-world discovery, novel chemotypes do not arrive in a pre-balanced ratio. Enforcing a target class distribution on a scaffold split requires discarding scaffolds or selectively filtering them, which biases the evaluation. By leaving the scaffold split unconstrained (except for size-balancing), we evaluate models on the natural distribution of novel chemistry, leading to a scientifically honest generalization assessment.

### Q5: What is the "Generalization Gap"?
*   **Answer:** The generalization gap is the difference in performance (specifically in Macro F1 and AUC) when a model is evaluated on a random split versus a scaffold split. A large drop in performance on the scaffold split indicates that the model has memorized specific structural components (overfitting to scaffolds seen in training) and fails to generalize to novel chemical scaffolds.

### Q6: What are Morgan fingerprints, and what do the parameters `radius=2` and `nBits=2048` mean?
*   **Answer:** Morgan fingerprints are circular topological representations of molecules.
    *   `radius=2` indicates that circular atom environments are captured up to a distance of 2 bonds away from each atom (equivalent to a diameter of 4, mimicking ECFP4).
    *   `nBits=2048` means the captured atom environments are hashed into a static bit vector of length 2048. If a specific substructural fragment is present, its hashed bit index is set to 1.

### Q7: Why are LogP and TPSA critical descriptors for BBB permeability?
*   **Answer:**
    *   **LogP (lipophilicity):** Molecules crossing the BBB must passively diffuse through lipid bilayers. Very hydrophilic compounds (low LogP) cannot cross, while excessively lipophilic compounds (high LogP) get trapped in the lipid membrane or bind non-specifically. The optimal LogP range for CNS drugs is typically between 1 and 3.
    *   **TPSA (Topological Polar Surface Area):** Measures the surface sum over all polar atoms (oxygen, nitrogen, etc.). High polarity prevents passage through membranes. CNS-active drugs typically require a TPSA $< 90\text{ Å}^2$ (and often $< 60\text{ Å}^2$).

### Q8: What does RDKit sanitization do, and why did two molecules fail?
*   **Answer:** Sanitization in RDKit is a series of checks (Kekulization, valence verification, aromaticity detection, ring checks) to ensure a molecule represents a chemically valid structure. Two molecules (`mepenzolatebromide` and `tiotidine`) failed because their SMILES strings contained a carbocation center `[C+]` bonded to an oxygen and two phenyl rings, resulting in an explicit valence greater than permitted for carbon under RDKit's valence rules.

### Q9: Why did you filter out the 10 dot-disconnected compounds instead of salt-stripping them?
*   **Answer:** When we inspected the dot-disconnected structures, they were not simple organic salts (like a sodium salt or a hydrochloride salt) where a simple stripping script is appropriate. They were complex co-drugs (sultamicillin), copolymer mixtures (colestipol), or complex solvates. Running standard descriptor calculations (such as molecular weight or TPSA) on disconnected graphs yields sum-aggregates that do not represent a single active molecule. Since they represent only 0.13% of the dataset, it was chemically cleaner to exclude them.

### Q10: How did you handle class imbalance in B3DB?
*   **Answer:** B3DB contains 63.5% BBB+ and 36.5% BBB- compounds. To prevent models from biasing towards BBB+:
    *   We prioritized **Macro F1-Score**, **ROC-AUC**, and **PR-AUC** over raw Accuracy.
    *   We enabled class weight balancing in Logistic Regression (`class_weight='balanced'`) and Random Forest, and set `scale_pos_weight` in XGBoost to penalize majority-class errors.

### Q11: What is the difference between ROC-AUC and PR-AUC? Why are they both used?
*   **Answer:**
    *   **ROC-AUC** plots True Positive Rate vs. False Positive Rate. It is insensitive to class distribution changes, representing a general ranking metric.
    *   **PR-AUC** plots Precision vs. Recall. It is highly sensitive to class imbalance. In drug screening where false positives are costly (e.g. testing an inactive compound in wet-labs), PR-AUC gives a better picture of model precision.

### Q12: Why did you select Logistic Regression, Random Forest, and XGBoost?
*   **Answer:**
    *   **Logistic Regression:** Standard baseline. Highly interpretable linear model.
    *   **Random Forest:** Non-linear bagging model. Robust to noise and outliers.
    *   **XGBoost:** Gradient-boosting model that builds trees sequentially to correct errors. Generally achieves the highest predictive accuracy among traditional ML algorithms.
    *   *Constraint:* Deep learning models were avoided due to the limited dataset size and to maintain high feature interpretability.

### Q13: What is the difference between global and local explainability?
*   **Answer:**
    *   **Global Explainability:** Identifies which features are most important across the entire dataset (e.g., Gini feature importances showing that TPSA and LogP are the top contributors for all compounds).
    *   **Local Explainability:** Explains why the model made a specific prediction for a single compound (e.g. using SHAP to show that paracetamol was predicted BBB- because its polar surface area pushed the probability down).

### Q14: How does the FastAPI backend integrate with the React frontend?
*   **Answer:** The React frontend acts as a client that sends HTTP POST requests containing SMILES strings to the FastAPI server. The backend validates the SMILES using RDKit, generates the molecule SVG, calculates descriptors, loads the pre-trained `.joblib` model pipeline, executes predictions, and returns a JSON response containing all coordinates, predictions, and SVGs for the frontend to render.

### Q15: Why is model serialization critical, and what is stored in the production `.joblib` file?
*   **Answer:** Serializing the model avoids retraining it every time an API request is made or the app is restarted — `joblib.load()` deserializes the fitted `RandomForestClassifier` directly into memory once, during FastAPI's lifespan startup. Because the selected production architecture is scale-invariant (tree-based splits don't depend on feature magnitude), the `.joblib` file stores **only the fitted classifier itself** — no `StandardScaler`, imputer, or `Pipeline` wrapper is bundled, since none is needed. A companion `production_metadata.json` stores the fixed 11-descriptor feature ordering, hyperparameters, and training environment versions, so the API can validate the loaded model matches the documented production specification on every startup (`ModelLoader.load()` in `backend/app/services/model_loader.py`).

### Q16: How does batch screening (Phase 9) avoid duplicating the single-prediction logic?
*   **Answer:** `POST /api/predict/batch` reuses the exact same `process_molecule()` function that `/api/predict` uses for RDKit parsing, canonicalization, and descriptor calculation, and reuses the same lifespan-loaded model instance — it is never reloaded per request. The only difference is that valid rows are batched into a single `(N, 11)` NumPy matrix and scored with one `model.predict()`/`predict_proba()` call instead of one call per molecule, which is far more efficient for up to 5,000 rows. SVG generation is skipped for batch rows (it's not needed for a results table and would bloat the response). Row-level errors — empty, malformed, or multi-component (`.`-containing) SMILES — are captured per row with an error message rather than dropping the row silently, so the original CSV row count and order are always preserved in the response.

### Q17: How does the single Docker container serve both the React frontend and the FastAPI backend on one port?
*   **Answer:** The multi-stage `Dockerfile` (Phase 12) first builds the React app to static HTML/JS/CSS in a `node:22-alpine` stage, then copies that build output into a `python:3.13-slim` stage alongside the FastAPI backend. At runtime, `backend/app/main.py` calls `app.mount("/", StaticFiles(directory=FRONTEND_DIST_PATH, html=True))` — but only if that directory actually exists on disk, and only *after* all `/api/*` routers have already been registered. Because FastAPI/Starlette resolves routes in registration order, requests to `/api/predict`, `/api/health`, etc. are always matched by the API routers first; anything else falls through to the static file mount, which serves `index.html` for the React SPA. This keeps local development (where no `frontend/dist` exists, since Vite serves the frontend separately on port 5173) completely unaffected by the same code path.
