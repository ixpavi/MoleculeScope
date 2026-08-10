# Evaluation Methodology Specification — MoleculeScope

This document outlines the splitting algorithms, baseline controls, and metric criteria used to evaluate model performance and generalization capabilities in **MoleculeScope**.

---

## 1. Random Stratified Split (80/20 Baseline)

*   **Rationale:** Simulates the condition where the training and testing sets are drawn from the same underlying distribution (in-distribution evaluation). Stratification ensures the raw class balance of B3DB is preserved exactly in both subsets.
*   **Parameters:**
    *   **Train Size:** 6,236 compounds (**80.00%**)
    *   **Test Size:** 1,559 compounds (**20.00%**)
    *   **Random Seed:** 42
*   **Stratified Class Distribution:**
    *   *Train set:* 3,962 BBB+ (63.53%) / 2,274 BBB- (36.47%)
    *   *Test set:* 991 BBB+ (63.57%) / 568 BBB- (36.43%)
*   **Index Artifact:** `splits/random_split_indices.json`

---

## 2. Bemis-Murcko Scaffold Split (Generalization Test)

*   **Rationale:** Simulates virtual screening of structurally novel chemical libraries (out-of-distribution evaluation). This measures the "generalization gap" and is the primary scientific metric for MoleculeScope.
*   **Parameters:**
    *   **Train Size:** 6,236 compounds (**80.00%**)
    *   **Test Size:** 1,559 compounds (**20.00%**)
    *   **Zero-Overlap Rule:** The intersection of scaffolds between the train and test sets is exactly empty.
    *   **Label Policy:** Natural class distribution is preserved. No label engineering was used to alter or balance the subsets.
*   **Scaffold-split Class Distribution:**
    *   *Train set:* 4,003 BBB+ (64.19%) / 2,233 BBB- (35.81%)
    *   *Test set:* 950 BBB+ (60.94%) / 609 BBB- (39.06%)
*   **Structural Composition:**
    *   *Total Unique Scaffolds:* 2,125 ring systems.
    *   *Acyclic Singletons:* 311 compounds (treated as individual unique groups to prevent cluster skew).
    *   *Scaffold Leakage / Overlap:* **0** (verified zero scaffold leakage).
*   **Index Artifact:** `splits/scaffold_split_indices.json`

---

## 3. Split-Aware Feature Alignment

To prevent feature leakage and preserve consistent evaluation across all representations, splitting is executed on sample indices (0-indexed integer offsets from 0 to 7794). These indices align map 1-to-1 with:
1.  **Cleaned Dataset:** Rows in `backend/data/processed/b3db_cleaned.csv`
2.  **Representation A:** Rows in `features/descriptors.csv`
3.  **Representation B:** Rows in `features/fingerprints.npz`
4.  **Representation C:** Rows in `features/combined.npz`

---

## 4. Preprocessing Leakage Prevention Rule

During scaling and modeling, the following pipeline sequence is strictly enforced:
1.  Load the train indices from the split JSON.
2.  Fit the `StandardScaler` (descriptors) and `MedianImputer` (if any NaNs occur) **only on the training indices**.
3.  Apply (transform) the fitted scales to the test indices.
4.  *Reason:* Fitting scalers on the full dataset leaks the mean and standard deviation of the test set into training, violating validation guidelines.

---

## 5. Evaluation Metrics

Model comparison will prioritize metrics robust to moderate class imbalance:
*   **Macro F1-Score:** Primary metric (unweighted mean of F1-scores of both classes).
*   **ROC-AUC:** Measures general class rank separation.
*   **PR-AUC:** Measures precision-recall tradeoffs (critical for virtual screening where minimizing false positives is essential).
*   **Confusion Matrix:** Displays counts of TP, FP, TN, FN.
