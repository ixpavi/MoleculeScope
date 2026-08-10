# Final Model Recommendation — MoleculeScope

Based on the empirical findings of Phase 4 and Phase 5, we evaluate model architectures and features to establish a final recommendation for production deployment.

---

## 1. Decision Matrix & Multi-Dimensional Tradeoffs

To make a scientifically defensible recommendation, we compare the top-performing models across three axes:

| Evaluation Axis | Random Forest (Descriptors) | XGBoost (Combined) | Logistic Regression (Combined) |
| :--- | :--- | :--- | :--- |
| **A. Scaffold Generalization** | **Best** (Macro F1 = **0.7212**, Accuracy = **74.47%**) | Moderate (Macro F1 = **0.6838**, Accuracy = **72.80%**) | Low (Macro F1 = **0.6668**, Accuracy = **71.46%**) |
| **B. Ranking & Discrimination** | Moderate (ROC-AUC = **0.8017**, PR-AUC = **0.8504**) | **Best** (ROC-AUC = **0.8138**, PR-AUC = **0.8684**) | Moderate (ROC-AUC = **0.7865**, PR-AUC = **0.8445**) |
| **C. Complexity & Latency** | **Excellent** (11 features. Low memory, instant RDKit parsing). | High (2,059 features. Dense NPZ mapping, higher latency). | High (2,059 features. Dense NPZ mapping, higher latency). |
| **D. Explainability (SHAP/MDI)** | **Excellent** (Direct mapping to 11 physical descriptors). | Hard (2,048 hashed bits are non-interpretable). | Hard (2,048 hashed bits are non-interpretable). |

---

## 2. Final Selected Model: Random Forest on Descriptors

We recommend **Random Forest trained on Physicochemical Descriptors Only** as the final deployment model for the MoleculeScope application.

### Rationale:
1.  **Robust Out-of-Distribution Generalization:** Random Forest on Descriptors achieved the highest Macro F1 (**0.7212**) and accuracy (**74.47%**) on the Bemis-Murcko scaffold split. Tree bagging over simple physical properties generalizes better to structurally novel chemical classes than models relying on sparse fingerprint configurations. **Statistical caveat (see `statistical_significance.md`):** the raw *accuracy* gap over XGBoost+Combined (74.47% vs. 72.80%) is not statistically distinguishable from chance by McNemar's exact test (p = 0.102). The *Macro F1* gap — this project's stated primary metric under class imbalance — **is** statistically significant by paired bootstrap (+0.0374, 95% CI [+0.0154, +0.0592], excludes zero). The selection rationale therefore rests specifically on the Macro F1 comparison, not on accuracy.
2.  **Fingerprint Generalization Defect:** Fingerprint-based models showed substantially poorer scaffold generalization than descriptor-based models in this dataset and experimental setup (RF fingerprints Macro F1 drops to **0.5546** under scaffold shift). This may reflect that circular fingerprints do not generalize as well to unseen ring configurations. Descriptors-only models showed greater robustness to scaffold shift than fingerprint-only models in our experiments.
3.  **Explainability for Drug Discovery:** RF on Descriptors allows direct mapping of feature importances to physical parameters (TPSA, LogP, HBD). In drug screening, knowing *why* a compound is predicted to cross the BBB is as important as the prediction itself.
4.  **Operational Simplicity:** The model utilizes only 11 inputs. There is no need to generate, index, and load 2048-bit sparse arrays in the FastAPI server, reducing latency and memory footprints.

---

## 3. Serialization and Production Package Plan

The production package for Phase 6 will contain:
1.  **Trained Model:** Random Forest Classifier (`results/models/rf_descriptors_scaffold_model.joblib`).
2.  **Imbalance Mitigation:** Natural distribution used (Random Forest was fit with `class_weight="balanced"` to handle the 63.5/36.5 split).
3.  **Preprocessing Requirements:** **Scale-free** (no standard scaler or column transformer needs to be bundled, as tree-based structures are scale-invariant, simplifying pipeline deployment).
4.  **Feature Vector:** 11 RDKit descriptors generated dynamically by the RDKit engine on the backend.
5.  **Target App Metrics:** Accuracy = **74.47%**, Macro F1 = **0.7212**, ROC-AUC = **0.8017** (scaffold split baseline).
