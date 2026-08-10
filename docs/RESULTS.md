# Experimental Results — MoleculeScope

This document acts as the central database of all metrics, splits, and parameters computed during modeling and evaluation.

---

## 1. Cleaned Dataset Distribution (Phase 1 Output)
*   **Total Cleaned Compounds:** 7,795
*   **BBB+ (Permeable):** 4,953 (63.54%)
*   **BBB- (Impermeable):** 2,842 (36.46%)
*   **Excluded Records:** 12 records (2 invalid structures + 10 multi-component compounds)

---

## 2. Split Specifications (Phase 3 Output)

### Stratified Random Split
*   **Train Size:** 6,236 (63.53% BBB+ / 36.47% BBB-)
*   **Test Size:** 1,559 (63.57% BBB+ / 36.43% BBB-)

### Scaffold Split (Zero Overlap)
*   **Train Size:** 6,236 (64.19% BBB+ / 35.81% BBB-)
*   **Test Size:** 1,559 (60.94% BBB+ / 39.06% BBB-)
*   **Total Unique Scaffolds:** 2,125 ring systems (plus 311 acyclic singletons)
*   **Scaffold Overlap Train/Test:** `0` (Verified)

---

## 3. Performance Metrics Database (Phase 4 Output)

### A. Random Stratified Split Results

| Feature Set | Model | Accuracy | Precision | Recall | F1 | Macro F1 | ROC-AUC | PR-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Descriptors** | Logistic Regression | 0.8069 | 0.7979 | 0.9324 | 0.8599 | 0.7747 | 0.8545 | 0.8831 |
| | Random Forest | 0.8736 | 0.8788 | 0.9294 | 0.9034 | 0.8604 | 0.9382 | 0.9590 |
| | XGBoost | 0.8602 | 0.8510 | 0.9455 | 0.8958 | 0.8417 | 0.9301 | 0.9520 |
| **Fingerprints**| Logistic Regression | 0.8653 | 0.8606 | 0.9405 | 0.8987 | 0.8488 | 0.9398 | 0.9604 |
| | Random Forest | 0.8435 | 0.8223 | 0.9617 | 0.8865 | 0.8172 | 0.9279 | 0.9527 |
| | XGBoost | 0.8621 | 0.8470 | 0.9556 | 0.8981 | 0.8425 | 0.9349 | 0.9574 |
| **Combined** | Logistic Regression | 0.8711 | 0.8671 | 0.9415 | 0.9028 | 0.8558 | 0.9466 | 0.9651 |
| | Random Forest | 0.8627 | 0.8522 | 0.9485 | 0.8978 | 0.8444 | 0.9411 | 0.9621 |
| | XGBoost | 0.8717 | 0.8693 | 0.9395 | 0.9030 | 0.8568 | 0.9458 | 0.9646 |

### B. Scaffold Split Results

| Feature Set | Model | Accuracy | Precision | Recall | F1 | Macro F1 | ROC-AUC | PR-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Descriptors** | Logistic Regression | 0.7300 | 0.7195 | 0.9126 | 0.8046 | 0.6837 | 0.7648 | 0.7903 |
| | Random Forest | 0.7447 | 0.7599 | 0.8495 | 0.8022 | 0.7212 | 0.8017 | 0.8504 |
| | XGBoost | 0.7255 | 0.7281 | 0.8768 | 0.7956 | 0.6888 | 0.7947 | 0.8457 |
| **Fingerprints**| Logistic Regression | 0.6876 | 0.6902 | 0.8842 | 0.7753 | 0.6316 | 0.7435 | 0.8172 |
| | Random Forest | 0.6684 | 0.6550 | 0.9632 | 0.7797 | 0.5546 | 0.7448 | 0.8277 |
| | XGBoost | 0.6934 | 0.6829 | 0.9274 | 0.7866 | 0.6211 | 0.7614 | 0.8345 |
| **Combined** | Logistic Regression | 0.7146 | 0.7106 | 0.8968 | 0.7929 | 0.6668 | 0.7865 | 0.8445 |
| | Random Forest | 0.7178 | 0.7037 | 0.9274 | 0.8002 | 0.6599 | 0.8044 | 0.8630 |
| | XGBoost | 0.7280 | 0.7206 | 0.9042 | 0.8021 | 0.6838 | 0.8138 | 0.8684 |

---

## 4. Generalization Gap Values (Random vs. Scaffold Split)

Preliminary comparison of macro performance degradation under scaffold shift:

*   **Best Model (By Scaffold Split Macro F1):** Random Forest on Descriptors
    *   *Macro F1 Gap:* 0.8604 $\rightarrow$ 0.7212 (**-0.1392** drop)
    *   *ROC-AUC Gap:* 0.9382 $\rightarrow$ 0.8017 (**-0.1365** drop)
    *   *PR-AUC Gap:* 0.9590 $\rightarrow$ 0.8504 (**-0.1086** drop)
*   **Best Model (By Scaffold Split ROC-AUC):** XGBoost on Combined Features
    *   *Macro F1 Gap:* 0.8568 $\rightarrow$ 0.6838 (**-0.1730** drop)
    *   *ROC-AUC Gap:* 0.9458 $\rightarrow$ 0.8138 (**-0.1320** drop)
    *   *PR-AUC Gap:* 0.9646 $\rightarrow$ 0.8684 (**-0.0962** drop)

---

## 5. Preliminary Feature Importances (Phase 4 MDI / Coefs)

### A. Random Forest Descriptor Importance (Mean Decrease in Impurity)
1.  **TPSA (Topological Polar Surface Area):** `0.2832`
2.  **H-Bond Donors:** `0.1151`
3.  **LogP (Lipophilicity):** `0.1149`
4.  **H-Bond Acceptors:** `0.0970`
5.  **Molecular Weight:** `0.0862`
6.  **Fraction CSP3:** `0.0841`
7.  **Rotatable Bonds:** `0.0622`
8.  **Heavy Atom Count:** `0.0578`
9.  **Ring Count:** `0.0430`
10. **Aromatic Ring Count:** `0.0324`
11. **Formal Charge:** `0.0239`

### B. XGBoost Descriptor Importance (Gain)
1.  **H-Bond Donors:** `0.1904`
2.  **Formal Charge:** `0.1818`
3.  **TPSA:** `0.1811`
4.  **Ring Count:** `0.0694`
5.  **H-Bond Acceptors:** `0.0650`
6.  **Aromatic Ring Count:** `0.0643`
7.  **Rotatable Bonds:** `0.0548`
8.  **Fraction CSP3:** `0.0535`
9.  **LogP:** `0.0501`
10. **Molecular Weight:** `0.0470`
11. **Heavy Atom Count:** `0.0426`

---

## 6. Model Recommendation & Retraining Strategy

### A. Evaluation vs. Production Model Distinction
*   **Evaluation Model:** The metrics reported in Section 3 and Section 4 represent the performance of the model trained and evaluated using the Bemis-Murcko scaffold split (6,236 train samples / 1,559 test samples). These metrics establish a strict, reproducible out-of-distribution generalization benchmark (Macro F1 = 0.7212, Accuracy = 74.47%).
*   **Production Model:** To maximize statistical power for actual deployment, the selected architecture (**Random Forest on 11 molecular descriptors**) has been retrained in Phase 6 on the full cleaned dataset of **7,795** molecules. Its performance is expected to equal or exceed the evaluation metrics, but it is not directly evaluated on a test set (which would violate validation rules).

### B. Phase 6 Retraining Workflow (Completed)
1.  **Select Final Architecture:** Select **Random Forest Classifier + 11 Physicochemical Descriptors** as the final deployment model.
2.  **Preserve Benchmark:** Preserve the held-out scaffold evaluation results (FPs, FNs, ROC/PR curves, and metrics) as the validation benchmark.
3.  **Full Dataset Training:** Retrain the selected architecture (retaining all baseline parameters: `n_estimators=250`, `max_depth=12`, `min_samples_split=5`, `min_samples_leaf=2`, `max_features='sqrt'`, `class_weight='balanced'`) on the full **7,795** cleaned molecules.
4.  **Serialization:** Serialize and save the retrained model as the final production model [production_model.joblib](file:///c:/MoleculeScope/backend/models/production_model.joblib) alongside its [production_metadata.json](file:///c:/MoleculeScope/backend/models/production_metadata.json) specifications.
