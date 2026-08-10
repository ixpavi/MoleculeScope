# Academic Report Outline — MoleculeScope

This document provides a comprehensive outline for the college project report, mapped directly to standard academic and scientific criteria.

---

# Title: MoleculeScope: Early-Stage Computational Screening of Blood-Brain Barrier Permeability Using Traditional Machine Learning

## 1. Abstract
*   Summarizes the clinical importance of blood-brain barrier (BBB) permeability.
*   Introduces the B3DB dataset.
*   States the feature representations (descriptors, circular fingerprints) and models (Logistic Regression, Random Forest, XGBoost).
*   Highlights key quantitative findings (generalization gap between random stratified vs. scaffold split).

## 2. Introduction
*   Contextualizes early-stage computational screening in drug discovery.
*   Discusses CNS therapeutic targets and safety screening.
*   Introduces machine learning as an alternative to expensive in vitro/in vivo assays.

## 3. Problem Statement & Motivation
*   Why predicting BBB permeability is a bottleneck.
*   The issue of "scaffold generalization": models showing high accuracy on random splits but failing on structurally novel scaffolds in the real world.

## 4. Objectives
*   Build a reproducible data processing pipeline.
*   Train baseline and tree ensemble traditional ML models.
*   Measure the generalization gap using Bemis-Murcko scaffolds.
*   Deploy a prototype scientific dashboard.

## 5. Related Work
*   Brief review of traditional QSAR (Quantitative Structure-Activity Relationship) modeling.
*   Review of BBBP and B3DB benchmarks in literature.

## 6. Dataset Specification
*   B3DB database overview: sources, sample counts, class imbalances.
*   Description of columns, thresholds, and experimental confidence groups.

## 7. Data Preprocessing & Cleaning
*   SMILES validation and sanitization using RDKit.
*   Deduplication findings.
*   Exclusion of RDKit invalid structures and multi-component mixtures/prodrugs.

## 8. Molecular Feature Engineering
*   Physicochemical descriptors definition and scaling.
*   Morgan fingerprints circular representation theory.
*   Hybrid feature combination.

## 9. Machine Learning Methodology
*   Model architectures: Logistic Regression (Ridge), Random Forest, XGBoost.
*   Hyperparameter tuning and regularization controls.
*   Explainability framework: Global Gini importances and local SHAP values.

## 10. Experimental Design & Evaluation Split
*   Baseline: Stratified Random Split (80/20).
*   Test: Scaffold Split using Bemis-Murcko scaffolds.
*   Metric definitions: Macro F1, ROC-AUC, PR-AUC, Accuracy, Confusion Matrix.

## 11. Results & Discussion

### 11.1 Full Model × Representation × Split Comparison
Source: `results/model_comparison.csv` (18 primary experiments + 2 majority-class baselines, 6,236 train / 1,559 test throughout).

| Model | Representation | Split | Accuracy | Macro F1 | ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Majority baseline | — | Random | 63.57% | 0.3886 | 0.500 | 0.8178 |
| Majority baseline | — | Scaffold | 60.94% | 0.3786 | 0.500 | 0.8047 |
| Logistic Regression | Descriptors | Random | 80.69% | 0.7747 | 0.8545 | 0.8831 |
| Random Forest | Descriptors | Random | 87.36% | 0.8604 | 0.9382 | 0.9590 |
| XGBoost | Descriptors | Random | 86.02% | 0.8417 | 0.9301 | 0.9520 |
| Logistic Regression | Fingerprints | Random | 86.53% | 0.8488 | 0.9398 | 0.9604 |
| Random Forest | Fingerprints | Random | 84.35% | 0.8172 | 0.9279 | 0.9527 |
| XGBoost | Fingerprints | Random | 86.21% | 0.8425 | 0.9349 | 0.9574 |
| Logistic Regression | Combined | Random | 87.11% | 0.8558 | 0.9466 | 0.9651 |
| Random Forest | Combined | Random | 86.27% | 0.8444 | 0.9411 | 0.9621 |
| XGBoost | Combined | Random | 87.17% | 0.8568 | 0.9458 | 0.9646 |
| Logistic Regression | Descriptors | Scaffold | 73.00% | 0.6837 | 0.7648 | 0.7903 |
| **Random Forest (selected)** | **Descriptors** | **Scaffold** | **74.47%** | **0.7212** | **0.8017** | **0.8504** |
| XGBoost | Descriptors | Scaffold | 72.55% | 0.6888 | 0.7947 | 0.8457 |
| Logistic Regression | Fingerprints | Scaffold | 68.76% | 0.6316 | 0.7435 | 0.8172 |
| Random Forest | Fingerprints | Scaffold | 66.84% | 0.5546 | 0.7448 | 0.8277 |
| XGBoost | Fingerprints | Scaffold | 69.34% | 0.6211 | 0.7614 | 0.8345 |
| Logistic Regression | Combined | Scaffold | 71.46% | 0.6668 | 0.7865 | 0.8445 |
| Random Forest | Combined | Scaffold | 71.78% | 0.6599 | 0.8044 | 0.8630 |
| XGBoost | Combined | Scaffold | 72.80% | 0.6838 | 0.8138 | 0.8684 |

### 11.2 The Generalization Gap
Every model loses accuracy and Macro F1 moving from the random stratified split to the Bemis-Murcko scaffold split, but the *size* of the drop depends heavily on feature representation:

*   **Descriptors-only models degrade least.** Random Forest on Descriptors: Macro F1 falls from 0.8604 (random) to 0.7212 (scaffold), a drop of **-0.1392**.
*   **Fingerprint-only models degrade most.** Random Forest on Fingerprints: Macro F1 falls from 0.8172 (random) to 0.5546 (scaffold), a drop of **-0.2626** — the largest gap of any model/representation pair tested.
*   **Combined features sit in between** but are dominated by descriptors-only on the metric that matters most for deployment (Macro F1 under scaffold shift): Random Forest on Combined scores 0.6599 vs. 0.7212 for Descriptors-only.

This is the paper's central empirical finding: *a model can look excellent under random-split evaluation and still generalize poorly to structurally novel chemistry* — which is exactly the regime a real prospective screening campaign operates in. See `docs/EVALUATION_METHODOLOGY.md` and `results/figures/generalization_gap_macro_f1.png` / `generalization_gap_roc_auc.png` for the full analysis and plots.

### 11.3 Final Model Selection
Random Forest on Descriptors was selected for production despite XGBoost on Combined scoring marginally higher on ROC-AUC (0.8138 vs. 0.8017) and PR-AUC (0.8684 vs. 0.8504), because Random Forest on Descriptors won on the metric prioritized for this deployment context (scaffold Macro F1: 0.7212 vs. 0.6838), uses 11 inputs instead of 2,059, requires no scaling, and offers direct physical explainability. Full decision matrix and rationale: `results/analysis/final_model_recommendation.md`.

**Is the gap real?** A post-hoc statistical check (`results/analysis/statistical_significance.md`, run against the already-saved Phase 5 predictions — no retraining) shows the two candidates disagree by more than chance on Macro F1 but not on raw accuracy:
*   McNemar's exact test on accuracy (RF-right/XGB-wrong = 130 vs. XGB-right/RF-wrong = 104): **p = 0.102**, not significant at α=0.05.
*   Paired bootstrap (2,000 resamples) on the Macro F1 difference: **+0.0374, 95% CI [+0.0154, +0.0592]**, excludes zero.

This sharpens the argument rather than weakening it: the case for Random Forest + Descriptors should be made on Macro F1 (where the advantage is statistically robust), not on the smaller and statistically inconclusive accuracy difference.

### 11.4 Error Analysis
On the scaffold-split evaluation model (`results/analysis/error_analysis.md`, `results/analysis/scaffold_error_properties.csv`):

| Group | n | Mean MW | Mean LogP | Mean TPSA | Mean HBD |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Correct | 1,161 | 339.82 | 2.59 | 69.57 | 1.55 |
| False Positives | 255 | 329.76 | 3.15 | 61.13 | 1.19 |
| False Negatives | 143 | 345.71 | 1.71 | 97.67 | 2.41 |

False negatives have a notably higher mean TPSA (97.67 Å² vs. 69.57 Å² for correct predictions) — a potential explanation is that these may be carrier-mediated (active transport) permeants that a passive-descriptor model cannot represent, since active transporters (e.g. LAT1, GLUT1) can move polar compounds across the barrier without matching passive permeability heuristics. False positives skew toward lower TPSA and higher LogP, consistent with compounds that look passively permeable by descriptor heuristics alone. These are documented as *potential* explanations, not proven mechanisms — see `docs/LIMITATIONS.md` for the exact cautious phrasing used throughout this project (e.g. "descriptors-only models showed greater robustness to scaffold shift than fingerprint-only models in our experiments," never a universal claim about either representation).

### 11.5 Explainability (Phase 10)
*   **Global importances** (frozen production model's own Gini `feature_importances_`, not the evaluation model): TPSA is the dominant driver (28.5%), followed by LogP (11.6%), H-Bond Donors (11.4%), and H-Bond Acceptors (9.7%) — together the four descriptors most tied to passive membrane permeability account for >60% of total importance, consistent with established BBB permeability heuristics (e.g. the "Rule of 5"-adjacent CNS-MPO guidelines).
*   **Local SHAP explanations** are available per-molecule via `POST /api/explain` and are additive by construction (`base_value + Σ shap_values == probability_bbb_plus`), letting a user see e.g. that Caffeine's BBB+ call is driven positively by low H-Bond Donors and moderate TPSA.

## 12. Web Application Prototype
*   React + TypeScript + FastAPI stack architecture, with a strict decoupling boundary: the React client never imports RDKit or scikit-learn — all chemistry and inference stay server-side (`docs/API.md`).
*   **Single Predictor** page: live SMILES entry, RDKit 2D structure rendering, 11-descriptor breakdown, and BBB+/BBB- probability display.
*   **Batch Screener** page (Phase 9): CSV upload (5 MB / 5,000-row limits, extra-column preservation), paginated/filterable/searchable results table, and CSV export — reuses the same frozen model and descriptor pipeline as the single predictor, with no model reload.
*   **Performance Dashboard**: held-out scaffold-split evaluation metrics, majority-class baselines, and the full model/representation comparison table, clearly separated from the production model (trained on all 7,795 molecules with no independent test metric claimed for it).
*   **Explainability Hub** (Phase 10): a global feature-importance chart (frozen model's Gini importances) on the Performance page, and a per-prediction SHAP contribution breakdown rendered automatically after each Single Predictor run.

## 13. Limitations & Future Scope
*   Computational prediction accuracy vs. biological transport mechanisms — the descriptor-only model cannot represent active transporters (P-gp efflux, LAT1/GLUT1 influx); see §11.4 error analysis.
*   RDKit valence limits — 2 of the original 7,807 B3DB rows fail RDKit parsing entirely and are excluded (`docs/DATA_PREPROCESSING.md`).
*   Multi-component/mixture SMILES (containing `.`) are excluded from both training and inference (single and batch) rather than silently split, since the modeling dataset itself excludes them.
*   Deployment: a multi-stage Dockerfile exists (Phase 12) and its FastAPI static-mount mechanism was verified locally, but a live `docker build`/`docker run` has not yet been executed — see `docs/DEPLOYMENT.md` §1 and §6.
*   Future scope (`docs/FUTURE_SCOPE.md`): probability calibration (Platt/Isotonic), transporter-aware feature expansion, graph-based/deep representation learning, numerical logBB regression on the ~1,058-compound subset with experimental values, and an interactive molecule-drawing canvas.

## 14. Conclusion
*   Final summary of which model/feature combination performed best.
*   Final statement on the necessity of scaffold-based evaluations in drug discovery.

## 15. References
*   Academic citations for B3DB, RDKit, SHAP, and standard ML algorithms.
