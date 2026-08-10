# Feature Engineering Summary — MoleculeScope

This document records the molecular feature generation results and quality control metrics for Phase 2.

---

## 1. Feature Dimensions Summary

*   **Total Molecules Processed:** 7795
*   **Representation A (Descriptors):** 11 features (recorded in `descriptors.csv`)
*   **Representation B (Fingerprints):** 2048 binary bits (recorded in `fingerprints.npz`)
*   **Representation C (Combined):** 2059 features (recorded in `combined.npz`)

---

## 2. Molecular Descriptors Statistics & Ranges

| Descriptor | NaN Count | Inf Count | Min | Max | Mean | Median | Std | Constant? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Molecular Weight | 0 | 0 | 6.94 | 1882.33 | 385.34 | 362.50 | 170.26 | False |
| LogP | 0 | 0 | -8.90 | 12.61 | 2.36 | 2.55 | 2.19 | False |
| TPSA | 0 | 0 | 0.00 | 662.41 | 86.95 | 72.60 | 67.65 | False |
| H-Bond Donors | 0 | 0 | 0.00 | 24.00 | 2.01 | 1.00 | 2.26 | False |
| H-Bond Acceptors | 0 | 0 | 0.00 | 33.00 | 5.30 | 4.00 | 3.66 | False |
| Rotatable Bonds | 0 | 0 | 0.00 | 53.00 | 4.77 | 4.00 | 3.64 | False |
| Ring Count | 0 | 0 | 0.00 | 16.00 | 3.27 | 3.00 | 1.61 | False |
| Aromatic Ring Count | 0 | 0 | 0.00 | 8.00 | 1.32 | 1.00 | 1.08 | False |
| Heavy Atom Count | 0 | 0 | 1.00 | 136.00 | 26.89 | 26.00 | 11.97 | False |
| Fraction CSP3 | 0 | 0 | 0.00 | 1.00 | 0.50 | 0.48 | 0.23 | False |
| Formal Charge | 0 | 0 | 0.00 | 3.00 | 0.02 | 0.00 | 0.15 | False |


---

## 3. Descriptor Correlation Analysis

High correlation ($r \ge 0.90$) identified between the following descriptors:

| Feature 1 | Feature 2 | Correlation ($r$) |
| :--- | :--- | :--- |
| Molecular Weight | Heavy Atom Count | 0.9856 |
| TPSA | H-Bond Acceptors | 0.9201 |


*Note:* These correlated descriptors are preserved in the raw feature matrix. Collinearity will be handled inside model-specific pipelines later (e.g., L2 regularization in Logistic Regression or tree-splitting in RF/XGBoost).

---

## 4. Morgan Fingerprints Quality Control

*   **Fingerprint Type:** Morgan Circular Fingerprint (ECFP4 equivalent)
*   **Radius:** 2 (Diameter = 4)
*   **Bit Count (`nBits`):** 2048
*   **Chirality Included:** False
*   **Output representation:** Binary bit vector (`int8`)
*   **NaN / Inf Counts:** 0 / 0
*   **Active Bits statistics:**
    *   Minimum active bits: 1
    *   Maximum active bits: 142
    *   Mean active bits: 47.71 (2.33% density)
    *   Median active bits: 47.00
*   **Determinism Verified:** YES (confirmed identical output vectors across separate iterations)

---

## 5. Example Molecules Sanity Checks

All molecular property calculations are executed dynamically in RDKit.

### Caffeine
*   **Raw SMILES:** `CN1C=NC2=C1C(=O)N(C(=O)N2C)C`
*   **Canonical SMILES:** `Cn1c(=O)c2c(ncn2C)n(C)c1=O`
*   **Fingerprint Bits Count:** 2048 (Active: 25)
*   **Descriptors:**
    *   Molecular Weight: `194.1940`
    *   LogP: `-1.0293`
    *   TPSA: `61.8200`
    *   H-Bond Donors: `0.0000`
    *   H-Bond Acceptors: `3.0000`
    *   Rotatable Bonds: `0.0000`
    *   Ring Count: `2.0000`
    *   Aromatic Ring Count: `2.0000`
    *   Heavy Atom Count: `14.0000`
    *   Fraction CSP3: `0.3750`
    *   Formal Charge: `0.0000`

### Aspirin
*   **Raw SMILES:** `CC(=O)Oc1ccccc1C(=O)O`
*   **Canonical SMILES:** `CC(=O)Oc1ccccc1C(=O)O`
*   **Fingerprint Bits Count:** 2048 (Active: 24)
*   **Descriptors:**
    *   Molecular Weight: `180.1590`
    *   LogP: `1.3101`
    *   TPSA: `63.6000`
    *   H-Bond Donors: `1.0000`
    *   H-Bond Acceptors: `3.0000`
    *   Rotatable Bonds: `2.0000`
    *   Ring Count: `1.0000`
    *   Aromatic Ring Count: `1.0000`
    *   Heavy Atom Count: `13.0000`
    *   Fraction CSP3: `0.1111`
    *   Formal Charge: `0.0000`

### Ibuprofen
*   **Raw SMILES:** `CC(C)Cc1ccc(cc1)C(C)C(=O)O`
*   **Canonical SMILES:** `CC(C)Cc1ccc(C(C)C(=O)O)cc1`
*   **Fingerprint Bits Count:** 2048 (Active: 25)
*   **Descriptors:**
    *   Molecular Weight: `206.2850`
    *   LogP: `3.0732`
    *   TPSA: `37.3000`
    *   H-Bond Donors: `1.0000`
    *   H-Bond Acceptors: `1.0000`
    *   Rotatable Bonds: `4.0000`
    *   Ring Count: `1.0000`
    *   Aromatic Ring Count: `1.0000`
    *   Heavy Atom Count: `15.0000`
    *   Fraction CSP3: `0.4615`
    *   Formal Charge: `0.0000`

### Paracetamol
*   **Raw SMILES:** `CC(=O)Nc1ccc(O)cc1`
*   **Canonical SMILES:** `CC(=O)Nc1ccc(O)cc1`
*   **Fingerprint Bits Count:** 2048 (Active: 20)
*   **Descriptors:**
    *   Molecular Weight: `151.1650`
    *   LogP: `1.3506`
    *   TPSA: `49.3300`
    *   H-Bond Donors: `2.0000`
    *   H-Bond Acceptors: `2.0000`
    *   Rotatable Bonds: `1.0000`
    *   Ring Count: `1.0000`
    *   Aromatic Ring Count: `1.0000`
    *   Heavy Atom Count: `11.0000`
    *   Fraction CSP3: `0.1250`
    *   Formal Charge: `0.0000`


