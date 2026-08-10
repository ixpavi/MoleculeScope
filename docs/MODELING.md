# Machine Learning Modeling Specification — MoleculeScope

This document outlines the machine learning models, training configurations, and pipeline sequences used in **MoleculeScope**.

---

## 1. Model Families & Baseline Configurations

We train three distinct families of traditional machine learning classifiers, locked to a global reproducibility seed of `42`:

### A. Logistic Regression (Baseline)
*   **Role:** Linear baseline classifier. Evaluates linear decision boundaries.
*   **Hyperparameters:**
    *   `C`: 0.1 (inverse regularization strength, set to provide moderate regularization and prevent overfitting).
    *   `penalty`: 'l2' (Ridge regularization).
    *   `solver`: 'lbfgs' (robust optimization solver).
    *   `max_iter`: 1000.
    *   `random_state`: 42.

### B. Random Forest
*   **Role:** Traditional bagging ensemble.
*   **Hyperparameters:**
    *   `n_estimators`: 250 (number of decision trees).
    *   `max_depth`: 12 (restricted to prevent deep over-fitting on high-dimensional sparse fingerprints).
    *   `min_samples_split`: 5.
    *   `min_samples_leaf`: 2.
    *   `max_features`: 'sqrt' (standard square root feature selection per split).
    *   `class_weight`: 'balanced' (scales weights inversely proportional to class frequencies to handle moderate imbalance).
    *   `random_state`: 42.

### C. XGBoost (Gradient Boosting)
*   **Role:** High-performance boosting ensemble.
*   **Hyperparameters:**
    *   `n_estimators`: 200.
    *   `max_depth`: 6 (standard maximum depth for tree boosting).
    *   `learning_rate`: 0.05 (slower learning rate paired with moderate tree count for stable convergence).
    *   `subsample`: 0.8 (fraction of samples randomly sampled per tree for regularization).
    *   `colsample_bytree`: 0.8 (fraction of features randomly sampled per tree).
    *   `min_child_weight`: 2.
    *   `eval_metric`: 'logloss'.
    *   `random_state`: 42.
    *   *Weighting:* No class weighting is applied (default parameters). XGBoost handles the moderate 63.5/36.5 imbalance without tuning class weights.

---

## 2. Preprocessing & Leakage Prevention Rules

To guarantee no test set parameters leak into training, scaling parameters are fit **only on training split indices** and subsequently applied to test slices.

### A. Representation A (Molecular Descriptors Only)
*   **Logistic Regression:** Standardized using `StandardScaler` (zero mean, unit variance) fit on training data.
*   **Random Forest / XGBoost:** No scaling (tree-based models are scale-invariant).

### B. Representation B (Morgan Fingerprints Only)
*   **All Models:** No scaling. Fingerprints are kept in their raw binary `int8` state. Standardizing sparse binary bits introduces dense floating-point columns and increases memory usage without improving signal.

### C. Representation C (Combined Features)
*   **Logistic Regression:** Custom partial scaling is applied. The first 11 columns (physicochemical descriptors) are standardized using a `StandardScaler` fit on training data. The remaining 2,048 columns (Morgan fingerprints) are left untouched in their binary state.
*   **Random Forest / XGBoost:** No scaling.

---

## 3. Imbalance Handling Policy
*   **imbalance ratio:** BBB+ = 63.54% / BBB- = 36.46% (moderate, 1.74 to 1 ratio).
*   **SMOTE / Oversampling:** Excluded from baseline modeling to prevent artificial sample generation.
*   **Imbalance mitigation:**
    *   *Random Forest:* Handled using `class_weight="balanced"`.
    *   *Logistic Regression / XGBoost:* Run on original class distributions.
    *   *Evaluation:* Focused on Macro F1, ROC-AUC, and PR-AUC instead of raw accuracy to prevent majority-class bias.

---

## 4. Reproducibility & Random Seeds
To ensure all experiments, splits, and training steps are fully reproducible, a global random state of `42` is locked for all models:
*   Train/Test splitting seed: `42`
*   Scikit-Learn models seed: `random_state=42`
*   XGBoost seed: `random_state=42`

---

## 5. Artifact Saving Strategy
Trained models are saved as unified `.joblib` objects in `results/models/`. Each file contains the trained classifier and the corresponding scaler object (if scaling was used):
*   `logistic_descriptors_random_model.joblib` / `logistic_descriptors_scaffold_model.joblib`
*   `rf_fingerprints_random_model.joblib` / `rf_fingerprints_scaffold_model.joblib`
*   `xgb_combined_random_model.joblib` / `xgb_combined_scaffold_model.joblib`
*(A total of 18 model files representing all experimental permutations are written).*

---

## 6. Production Model Packaging & Serialization (Phase 6)

### A. Selected Deployment Model
Following detailed evaluation in Phase 5, the final selected architecture is **Random Forest Classifier trained on 11 Physicochemical Descriptors**.
*   **Training Dataset:** Retrained on the complete cleaned dataset of **7,795** compounds (to maximize statistical signal for production deployment).
*   **Target Mapping:** `BBB+` $\rightarrow$ 1, `BBB-` $\rightarrow$ 0.
*   **Preprocessing:** **Scale-free** (no standardization or scaling transformations needed, as Random Forest is scale-invariant).
*   **Hyperparameters:**
    *   `n_estimators`: 250
    *   `max_depth`: 12
    *   `min_samples_split`: 5
    *   `min_samples_leaf`: 2
    *   `max_features`: 'sqrt'
    *   `class_weight`: 'balanced'
    *   `random_state`: 42

### B. Serialization Package
The production model is serialized as a deployable package located at:
*   Model file: [production_model.joblib](file:///c:/MoleculeScope/backend/models/production_model.joblib)
*   Metadata file: [production_metadata.json](file:///c:/MoleculeScope/backend/models/production_metadata.json)

The accompanying metadata specifies the exact RDKit descriptor definitions, training environment versions (scikit-learn, rdkit, Python), target mapping, and the baseline scaffold evaluation benchmark for reference.

### C. Phase 6 Serialization Workflow
The model is serialized via the following workflow:
```text
Select final architecture (Random Forest + 11 Descriptors)
    ↓
Preserve Phase 5 scaffold evaluation benchmark artifacts (reproducible metrics)
    ↓
Retrain Random Forest + 11 descriptors on all 7,795 cleaned molecules
    ↓
Save final production model and metadata package (production_model.joblib)
```

### D. No New Performance Claims
Because the production model is trained on all 7,795 molecules, there is no independent test set. No independent metrics (accuracy, Macro F1, or ROC-AUC) are claimed for this retrained model. It is described as:
> "Retrained on the complete cleaned dataset after model selection, using the architecture validated through the Phase 5 scaffold-split evaluation."
The scaffold-split evaluation model metrics (Accuracy = 74.47%, Macro F1 = 0.7212, ROC-AUC = 0.8017) are preserved strictly as the reference baseline.

