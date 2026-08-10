# Preprocessing Summary — MoleculeScope

This document records the data cleaning results and statistics for the B3DB database in Phase 1.

---

## 1. Dataset Dimensions Before and After

| Stage | Row Count | Column Count |
| :--- | :--- | :--- |
| **Raw B3DB (Source)** | 7807 | 12 |
| **Cleaned (Processed)** | 7795 | 13 (including canonical_smiles) |

---

## 2. Final Class Distribution

| Class Label | Compound Count | Percentage |
| :--- | :--- | :--- |
| **BBB+ (Permeable)** | 4953 | 63.54% |
| **BBB- (Impermeable)** | 2842 | 36.46% |
| **Total** | 7795 | 100.00% |

---

## 3. Exclusion Registry

The following 12 compounds were excluded during preprocessing:

| Index | Name | Class | Type | Reason |
| :--- | :--- | :--- | :--- | :--- |
| 5043 | mepenzolatebromide | BBB- | Invalid SMILES | Fails RDKit valence check (carbocation valence error on [C+]) |
| 7737 | tiotidine | BBB- | Invalid SMILES | Fails RDKit valence check (carbocation valence error on [C+]) |
| 1361 | sultamicillin | BBB- | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |
| 1458 | eqvalan | BBB- | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |
| 1932 | nan | BBB+ | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |
| 5538 | colestipol | BBB- | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |
| 6008 | nan | BBB+ | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |
| 6257 | nan | BBB- | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |
| 6428 | nan | BBB- | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |
| 6429 | nan | BBB- | Multi-component | Contains 3 disconnected structures (mixtures/prodrugs/copolymers) |
| 6703 | nan | BBB- | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |
| 6704 | nan | BBB+ | Multi-component | Contains 2 disconnected structures (mixtures/prodrugs/copolymers) |

---

## 4. Specific Record Anomalies

### Mepenzolate Bromide vs. Tiotidine
*   **The Issue:** `tiotidine` (index 7737) is structurally inconsistent with its database record. It contains the chemical structure of mepenzolate bromide (without chirality) instead of tiotidine. 
*   **The Solution:** Both structures contain carbocation transcription errors (`[C+]`) which fail RDKit parsing. Since tiotidine is chemically erroneous and cannot be repaired safely, both records have been excluded from modeling.

## 5. Multi-component Exclusions Rationale
Dot-disconnected structures represent physical mixtures of active ingredients, copolymers, or complexes. Molecular descriptors computed on disconnected graphs yield aggregated sums (e.g., the molecular weight is the sum of both components) which does not represent a single chemical entity crossing the blood-brain barrier. All 10 compounds were excluded to ensure modeling integrity.
