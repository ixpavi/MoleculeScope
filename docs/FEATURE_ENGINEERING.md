# Feature Engineering Specification — MoleculeScope

This document outlines the molecular representations engineered in Phase 2 for training traditional machine learning models. All statistics and ranges are derived from the cleaned dataset of 7,795 compounds.

---

## 1. Physicochemical Descriptors (Representation A)

We extract 11 interpretable molecular descriptors using RDKit's `rdMolDescriptors`, `Descriptors`, and `Chem` modules:

| Descriptor Name | RDKit function | Chemical Properties Captured |
| :--- | :--- | :--- |
| **Molecular Weight** | `Descriptors.MolWt` | Molecule size and bulkiness. |
| **LogP** | `Descriptors.MolLogP` | Lipophilicity (Wildman-Crippen partition coefficient). |
| **TPSA** | `Descriptors.TPSA` | Topological polar surface area (polarity, critical for BBB crossing). |
| **H-Bond Donors** | `Descriptors.NumHDonors` | Number of hydrogen-bond donor groups. |
| **H-Bond Acceptors** | `Descriptors.NumHAcceptors` | Number of hydrogen-bond acceptor groups. |
| **Rotatable Bonds** | `Descriptors.NumRotatableBonds` | Conformational flexibility of the molecule. |
| **Ring Count** | `Descriptors.RingCount` | Total number of ring structures. |
| **Aromatic Ring Count** | `Descriptors.NumAromaticRings` | Number of aromatic rings. |
| **Heavy Atom Count** | `Descriptors.HeavyAtomCount` | Count of non-hydrogen atoms. |
| **Fraction CSP3** | `Descriptors.FractionCSP3` | Ratio of sp3 hybridized carbons to total carbons (saturation indicator). |
| **Formal Charge** | `Chem.GetFormalCharge` | Net charge. Highly charged molecules rarely cross the BBB. |

### Descriptor Range & Statistics (Computed over 7,795 rows)

| Descriptor | NaN Count | Inf Count | Min | Max | Mean | Median | Std | Constant? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Molecular Weight** | 0 | 0 | 6.94 | 1,882.33 | 385.34 | 362.50 | 170.26 | False |
| **LogP** | 0 | 0 | -8.90 | 12.61 | 2.36 | 2.55 | 2.19 | False |
| **TPSA** | 0 | 0 | 0.00 | 662.41 | 86.95 | 72.60 | 67.65 | False |
| **H-Bond Donors** | 0 | 0 | 0.00 | 24.00 | 2.01 | 1.00 | 2.26 | False |
| **H-Bond Acceptors** | 0 | 0 | 0.00 | 33.00 | 5.30 | 4.00 | 3.66 | False |
| **Rotatable Bonds** | 0 | 0 | 0.00 | 53.00 | 4.77 | 4.00 | 3.64 | False |
| **Ring Count** | 0 | 0 | 0.00 | 16.00 | 3.27 | 3.00 | 1.61 | False |
| **Aromatic Ring Count** | 0 | 0 | 0.00 | 8.00 | 1.32 | 1.00 | 1.08 | False |
| **Heavy Atom Count** | 0 | 0 | 1.00 | 136.00 | 26.89 | 26.00 | 11.97 | False |
| **Fraction CSP3** | 0 | 0 | 0.00 | 1.00 | 0.50 | 0.48 | 0.23 | False |
| **Formal Charge** | 0 | 0 | 0.00 | 3.00 | 0.02 | 0.00 | 0.15 | False |

---

## 2. Descriptor Collinearity Results

We computed the pairwise correlation matrix over the 11 descriptors. The following pairs showed high collinearity ($r \ge 0.90$):

| Feature 1 | Feature 2 | Correlation ($r$) |
| :--- | :--- | :--- |
| **Molecular Weight** | **Heavy Atom Count** | 0.9856 |
| **TPSA** | **H-Bond Acceptors** | 0.9201 |

*Note on Mitigation:* To avoid feature leakage, we preserve the complete 11-descriptor matrix in `features/descriptors.csv`. Dropping redundant features (such as `HeavyAtomCount` or `H-Bond Acceptors`) to stabilize linear classifiers like Logistic Regression will be implemented during Phase 3/4 pipeline fitting, restricted to training data only.

---

## 3. Morgan Fingerprints (Representation B)

*   **Type:** Morgan Circular Fingerprints (approximate equivalent of ECFP4).
*   **Parameters:**
    *   **Radius:** 2 (captures circular environments around each atom up to 2 bonds away).
    *   **Bit Count (`nBits`):** 2048.
    *   **Chirality Included:** False.
    *   **Output Representation:** Binary bit vector (`int8`), where 1 indicates the presence of a specific chemical substructure and 0 indicates absence.
*   **RDKit API:** `rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048, useChirality=False)`

### Quality Control & Statistics (Computed over 7,795 rows)
*   **Dimensionality Verification:** Every parsed molecule successfully generated a 2048-bit vector.
*   **Missing / Infinite Values:** 0 NaNs and 0 Infs.
*   **Active Bit Counts:**
    *   *Minimum:* 1 active bit (found in very small molecules, e.g. methane-like or diatomic compounds)
    *   *Maximum:* 142 active bits
    *   *Mean:* 47.71 active bits (2.33% bit density)
    *   *Median:* 47.00 active bits
*   **Determinism:** Verified. Generating fingerprints twice on control SMILES (Caffeine) returned identical bit arrays.

---

## 4. Hybrid Representation (Representation C)

*   **Definition:** Concatenation of the 11 scaled molecular descriptors and the 2048-bit Morgan circular fingerprint.
*   **Final Dimensionality:** **2,059** features.
*   *Implementation:* Combined as a 2D float64 array of shape `(7795, 2059)` stored in `features/combined.npz`.

---

## 5. Feature Engineering Artifact Location

All outputs are generated programmatically and saved to:
*   **Descriptors CSV:** `features/descriptors.csv`
*   **Fingerprints NPZ:** `features/fingerprints.npz`
*   **Combined NPZ:** `features/combined.npz`
*   **Machine-Readable Metadata:** `features/feature_metadata.json`
*   **Human-Readable Summary:** `features/feature_summary.md`
