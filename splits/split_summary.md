# Dataset Splitting Summary — MoleculeScope

This document outlines the sizes, class distributions, and characteristics of the baseline Random Split and the generalization Scaffold Split.

---

## 1. Random Stratified Split (80/20 Baseline)

The random stratified split preserves the original dataset class balance (approximately 63.5% BBB+ / 36.5% BBB-) in both subsets.

*   **Enforced Random Seed:** 42
*   **Total Cleaned Molecules:** 7795

| Split Subset | Molecule Count | BBB+ Count | BBB- Count | BBB+ Ratio | BBB- Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train Set** | 6236 | 3962 | 2274 | 63.53% | 36.47% |
| **Test Set** | 1559 | 991 | 568 | 63.57% | 36.43% |

*Verification:*
*   Scaffold Overlap: N/A (random division)
*   Split Overlap: **0** molecules overlap between train and test.

---

## 2. Bemis-Murcko Scaffold Split (Generalization Split)

The scaffold split groups compounds by their Bemis-Murcko ring-and-linker systems, ensuring that no scaffold in the test set has ever been seen during training.

*   **Target Split Ratio:** 80% Train / 20% Test
*   **Acyclic Molecules Handling:** Acyclic molecules have no rings (empty scaffold) and are treated as unique singleton groups (each acyclic compound represents its own scaffold class) to prevent a massive acyclic cluster from biasing the split ratio.
*   **Label Policy:** Natural class distribution is preserved. Target labels were **NOT** used to optimize the split or engineer balance.

| Split Subset | Molecule Count | BBB+ Count | BBB- Count | BBB+ Ratio | BBB- Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train Set** | 6236 | 4003 | 2233 | 64.19% | 35.81% |
| **Test Set** | 1559 | 950 | 609 | 60.94% | 39.06% |

### Scaffold Statistics
*   **Total Unique Scaffolds:** 2125
*   **Acyclic Singleton Molecules:** 311
*   **Scaffold Overlap Count:** **0** (verified zero scaffold leakage between sets)

---

## 3. Generalization Split Observation & Insights

### A. Size Alignment
The deterministic greedy bin-packing algorithm successfully achieved the target ratio:
*   **Actual Scaffold Train Ratio:** 80.00%
*   **Actual Scaffold Test Ratio:**  20.00%

### B. Natural Class Distribution Shift
In the scaffold split, we observe the natural class balance shift:
*   *Random Split Test Set:* 63.57% BBB+ / 36.43% BBB-
*   *Scaffold Split Test Set:* 60.94% BBB+ / 39.06% BBB-
*   *Observation:* 2125 unique scaffolds were grouped. The scaffold test set has a natural distribution that reflects structural class grouping. We preserve this natural imbalance to test how our classifiers perform under true out-of-distribution conditions without artificial balance manipulation.
