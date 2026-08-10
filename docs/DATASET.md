# Dataset Specification — B3DB (Blood-Brain Barrier Database)

This document records the specifications and characteristics of the raw dataset used in **MoleculeScope**. All statistics and metrics correspond to empirical results from the dataset verification phase.

---

## 1. Dataset Source & Metadata
*   **Legitimate URL:** `https://github.com/theochem/B3DB`
*   **Raw Data Path:** `https://raw.githubusercontent.com/theochem/B3DB/master/B3DB/B3DB_classification.tsv`
*   **Version:** B3DB Classification Dataset v1.0 (from master branch)
*   **Dimensions:** 7,807 rows, 12 columns
*   **Index Key:** `NO.` (values 1 to 7807)

---

## 2. Row Schema & Column Definitions

The dataset contains the following 12 columns:

| Column Name | Data Type | Null Count | Description |
| :--- | :--- | :--- | :--- |
| `NO.` | Integer | 0 | Unique sequential row index. |
| `compound_name` | String | 154 | Common drug or chemical identifier name. |
| `IUPAC_name` | String | 163 | Standard IUPAC name of the molecule. |
| `SMILES` | String | 0 | Simplified Molecular Input Line Entry System string (containing stereocenters). |
| `CID` | Float / Int | 2,752 | PubChem Compound ID. |
| `logBB` | Float | 6,749 | Experimental logarithm of brain-to-blood partition coefficient (nullable). |
| `BBB+/BBB-` | String (Categorical) | 0 | Permeability status: **BBB+** (crosses barrier) or **BBB-** (does not cross). |
| `Inchi` | String | 0 | International Chemical Identifier (InChI) string. |
| `threshold` | Float | 0 | logBB threshold value used to define BBB classification. |
| `reference` | String | 0 | Bibliographic reference database or publication source code. |
| `group` | String (Categorical) | 0 | Experimental agreement group. **A** (highest confidence), **B** (moderate), **C** (lowest). |
| `comments` | String | 7,651 | Quality notes, phase remarks, or experimental parameters. |

---

## 3. Statistical Distribution (Raw File)

### Class Distribution (Target Label `BBB+/BBB-`)
The raw dataset has a moderate imbalance favoring barrier-permeable compounds:
*   **BBB+ (Permeable):** 4,956 compounds (**63.48%**)
*   **BBB- (Impermeable):** 2,851 compounds (**36.52%**)
*   **Total Records:** 7,807 rows

### Missing Value Analysis
*   **SMILES:** 0 missing values.
*   **BBB+/BBB-:** 0 missing values.
*   **CID:** 2,752 missing values (35.25%).
*   **logBB:** 6,749 missing values (86.45%). This confirms why numerical regression modeling is unsuitable for the primary MVP and must be treated as an optional future extension.

---

## 4. Cheminformatics Analysis & Structural Quality Issues

RDKit structure checks were run on all 7,807 SMILES. The following issues were identified:

### A. Invalid SMILES (2 compounds)
Exactly two records fail RDKit molecule sanitization:

1.  **Row index 5043 (`mepenzolatebromide`):**
    *   *SMILES:* `C[N+]1(C)CCC[C@H](OC(=O)[C+](O)(c2ccccc2)c2ccccc2)C1`
    *   *RDKit Failure:* `Explicit valence for atom # 10 C, 4, is greater than permitted.`
    *   *Diagnosis:* The carbocation structure `[C+](O)` is rejected by RDKit's strict chemical valence engine.
2.  **Row index 7737 (`tiotidine`):**
    *   *SMILES:* `C[N+]1(C)CCCC(OC(=O)[C+](O)(c2ccccc2)c2ccccc2)C1`
    *   *RDKit Failure:* `Explicit valence for atom # 10 C, 4, is greater than permitted.`
    *   *Diagnosis:* In B3DB, this entry has been mistakenly assigned the structure of mepenzolate bromide (without chirality). The actual structure of tiotidine (an H2 antagonist containing an aminothiadiazole-like system) is missing from this entry, representing a label structural error at source.

*Action:* Both rows will be dropped during Phase 1 cleaning.

### B. Multi-Component & Dot-Disconnected SMILES (10 compounds)
Exactly 10 rows contain dot-disconnected components (`.` character in the SMILES string). Rather than salt-stripping, these were inspected and determined to be complex co-drugs, mixtures, or polymers rather than simple organic molecules with small counterions:

1.  `sultamicillin` (BBB-): Double drug linking ampicillin and sulbactam.
2.  `eqvalan` (BBB-): A multi-component mixture of ivermectin derivatives.
3.  `colestipol` (BBB-): A copolymer containing epichlorohydrin and diethylenetriamine.
4.  Two entries labeled `nan` (BBB+): Multi-component complexes (e.g., `CNO.Cc1oc...`).

*Action:* Because these dot-disconnected entries represent mixtures and co-drugs where standard descriptor calculations (such as molecular weight and polar surface area) would yield sum-aggregates rather than molecular properties, and because they represent a tiny portion of the dataset (0.13%), they will be filtered out during Phase 1. No automatic salt-stripping will be applied, preserving the rest of the 7,795 single-component organic compounds in their original protonation/isomer state.

### C. Duplicate Analysis
*   **Raw duplicate SMILES strings:** 0 duplicates.
*   **RDKit canonical SMILES duplicates:** 0 duplicates.
*   *Conclusion:* The dataset has been deduplicated by the curators before publication. No duplicate structures or conflicting labels exist in the raw dataset.
