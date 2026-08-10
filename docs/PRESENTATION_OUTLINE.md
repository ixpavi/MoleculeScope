# Presentation Slide Outline — MoleculeScope

This document outlines a 14-slide deck for defending the **MoleculeScope** project.

---

### Slide 1: Title Slide
*   **Title:** MoleculeScope: Machine Learning for Early-Stage Blood-Brain Barrier (BBB) Permeability Screening
*   **Sub-title:** Evaluating the Generalization Gap via Scaffold Splitting
*   **Presenter:** [Student Name]
*   **Affiliation:** [College Name]

### Slide 2: The Biological Challenge
*   **Key Concept:** What is the Blood-Brain Barrier?
*   **Context:** CNS-active drug candidates must cross the barrier (BBB+); non-CNS drug candidates should be barred (BBB-) to prevent side effects.
*   **Problem:** Experimental assays are expensive and slow.

### Slide 3: The Computational Solution
*   **Core Approach:** Early-stage computational screening.
*   **Pipeline:** SMILES $\rightarrow$ RDKit Features $\rightarrow$ Machine Learning Classifier $\rightarrow$ Predicted Permeability.
*   **Goal:** Provide quick, low-cost screening of massive chemical libraries.

### Slide 4: Core Research Questions
*   **RQ1:** Which ML model performs best (Logistic Regression vs. Random Forest vs. XGBoost)?
*   **RQ2:** Which representation is strongest (Descriptors vs. Morgan Fingerprints vs. Combined)?
*   **RQ3:** What is the "Generalization Gap" under scaffold split conditions?
*   **RQ4:** What features drive the model predictions?

### Slide 5: The B3DB Dataset (Phase 0 Findings)
*   **Source:** Blood-Brain Barrier Database (B3DB) containing 7,807 raw rows.
*   **Class Balance:** 63.48% BBB+ (4,956) / 36.52% BBB- (2,851).
*   **Columns:** SMILES structure, experimental groups (A, B, C), and nullable logBB values.

### Slide 6: Preprocessing & Data Cleaning
*   **Invalid Structures:** 2 invalid structures containing RDKit carbocation valence errors excluded.
*   **Mixture Filtering:** 10 dot-disconnected compounds (complex mixtures, prodrugs) excluded.
*   **Deduplication:** 0 raw or canonical duplicates (pre-deduplicated at source).

### Slide 7: Feature Engineering
*   **11 Physicochemical Descriptors:** MW, LogP, TPSA, Donors/Acceptors, Rotatable Bonds, Rings, Saturation, Charge.
*   **2048-bit Morgan Fingerprints:** Radius = 2 (ECFP4 equivalents) binary bit vectors.
*   **Concatenated Hybrid Features:** Physicochemical + substructural information combined.

### Slide 8: Evaluation Split Methodology
*   **Stratified Random Split (Baseline):** 80/20 split; preserves class distribution.
*   **Scaffold Split (Generalization Test):** Groups compounds by Bemis-Murcko scaffolds. Zero scaffold overlap between train and test. Emphasizes Macro F1, ROC-AUC, and PR-AUC.

### Slide 9: Traditional Machine Learning Models
*   **Logistic Regression:** L2 regularized linear baseline.
*   **Random Forest:** Non-linear bagger ensemble.
*   **XGBoost:** Gradient-boosted decision tree ensemble.
*   *Note:* No deep learning to maintain high interpretability and avoid overfitting on small datasets.

### Slide 10: Experimental Results
*   **Random split (best case):** Random Forest + Descriptors — 87.36% Accuracy, Macro F1 = 0.8604, ROC-AUC = 0.9382.
*   **Scaffold split (production-relevant):** Random Forest + Descriptors — 74.47% Accuracy, Macro F1 = **0.7212**, ROC-AUC = 0.8017, PR-AUC = 0.8504.
*   **Selected model + representation:** Random Forest on 11 physicochemical descriptors — wins scaffold Macro F1 over XGBoost+Combined (0.7212 vs. 0.6838) and Logistic+Combined (vs. 0.6668), while using 11 inputs instead of 2,059. (Full table: `results/model_comparison.csv`.)

### Slide 11: The Generalization Gap
*   Random Forest + Descriptors: Macro F1 drops from **0.8604 → 0.7212** (random → scaffold), a **-0.1392** gap.
*   Random Forest + Fingerprints: Macro F1 drops from **0.8172 → 0.5546**, a **-0.2626** gap — the worst of any model tested.
*   **Interpretation:** Fingerprint-based models pattern-match on training-set structural motifs and generalize worse to unseen scaffolds; physicochemical descriptors capture more transferable chemistry. This is why the scaffold split, not the random split, is the headline metric for this project.

### Slide 12: Model Interpretability (Phase 10)
*   **Global feature importances** (frozen production model's own Gini importances): TPSA (28.5%) > LogP (11.6%) > H-Bond Donors (11.4%) > H-Bond Acceptors (9.7%) — the top 4 descriptors most associated with passive membrane permeability account for >60% of total importance.
*   **Local SHAP explanations** (`POST /api/explain`): per-molecule, additive contributions toward BBB+ (base value + Σ contributions = predicted probability), shown live in the Predictor tab after every prediction.
*   **Error pattern:** False negatives have much higher mean TPSA (97.67 Å²) than correct predictions (69.57 Å²) — a potential explanation is carrier-mediated (active transport) permeants the model can't represent, not a proven mechanism.

### Slide 13: MoleculeScope Web App Prototype
*   *Visual interface walkthrough.*
*   **Backend:** FastAPI serving `/api/predict`, `/api/predict/batch` (Phase 9), `/api/explain` + `/api/explain/global` (Phase 10), and `/api/health` — all backed by one frozen, lifespan-loaded production model.
*   **Frontend:** React (Vite) + TypeScript dark laboratory dashboard with four views: **Single Predictor**, **Batch Screener** (CSV upload → paginated results → CSV export), **Performance Dashboard**, and per-prediction **SHAP explanations**.
*   **Testing:** 33 backend pytest cases (91% coverage of `backend/app`) + 23 frontend Vitest cases (67% coverage of `src/components`), all passing; verified end-to-end in a live browser session against a running backend.

### Slide 14: Conclusions, Deployment & Future Scope
*   **Takeaway:** Model evaluations must use scaffold splits, not random splits, to avoid over-optimistic performance reports — the two splits disagree by up to 26 points of Macro F1 depending on representation.
*   **Deployment status:** A multi-stage Dockerfile (Phase 12) has been authored and its FastAPI static-mount mechanism verified locally; a live `docker build` is the next concrete step before hosting.
*   **Future work:** Probability calibration, transporter-aware features, graph/deep representation learning, numerical logBB regression, and an interactive molecule-drawing canvas (`docs/FUTURE_SCOPE.md`).
