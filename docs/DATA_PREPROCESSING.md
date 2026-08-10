# Data Preprocessing Specification — MoleculeScope

This document outlines the strict cleaning and validation pipeline implemented in Phase 1 to prepare the B3DB database for feature engineering and model training.

---

## 1. Cleaning & Validation Pipeline Steps

A reproducible cleaning script will load `backend/data/B3DB_classification_raw.tsv` and process it using the following steps:

1.  **SMILES Validation:** Attempt to parse each raw SMILES string using RDKit's `Chem.MolFromSmiles`. Drop any rows that fail and log their names and SMILES.
2.  **Canonicalization:** Generate standard canonical SMILES using RDKit to ensure structural consistency.
3.  **Deduplication:** Search for duplicates using canonical SMILES.
4.  **Multi-Component Filtering:** Filter out molecules whose SMILES contain a dot (`.`), which represents mixtures, co-drugs, or copolymers.
5.  **Output Generation:** Export the clean, single-component, validated dataframe to `backend/data/B3DB_classification_cleaned.tsv`.

---

## 2. Invalid Structure Detail

During Phase 0 inspection, exactly **2 invalid structures** were identified and will be excluded:

*   **Row index 5043 (`mepenzolatebromide`):**
    *   *SMILES:* `C[N+]1(C)CCC[C@H](OC(=O)[C+](O)(c2ccccc2)c2ccccc2)C1`
    *   *RDKit Failure:* `Explicit valence for atom # 10 C, 4, is greater than permitted.`
    *   *Chemical Reason:* The carbocation center `[C+]` has 3 explicit bonds and 1 implicit charge, violating RDKit's standard valence checks for carbon.
*   **Row index 7737 (`tiotidine`):**
    *   *SMILES:* `C[N+]1(C)CCCC(OC(=O)[C+](O)(c2ccccc2)c2ccccc2)C1`
    *   *RDKit Failure:* Same as above.
    *   *Database Issue:* In B3DB, the structure associated with tiotidine is a duplicate of mepenzolate bromide (without chirality). This is a structural error at source.

---

## 3. Salt and Mixture Handling Policy

A common preprocessing step is to automatically strip salts (using RDKit's `SaltRemover`) and isolate the largest organic fragment. In our analysis, we did not apply automatic salt stripping for the following reasons:

*   **Dot-Disconnected Inspection:** Exactly 10 compounds contain dots (`.`) in their SMILES.
*   **Inspection Results:**
    *   `sultamicillin`: A mutual prodrug combining ampicillin and sulbactam. Removing one component would change the molecule's overall pharmacokinetic identity.
    *   `eqvalan`: A combination mixture of ivermectin components.
    *   `colestipol`: A polymer copolymer mixture.
    *   The other entries represent complex organic drug pairs or solvates rather than standard simple organic salts (like hydrochloride or sodium salts).
*   **Final Decision:** Because these 10 entries represent complex mixtures, co-drugs, or polymers where standard single-molecule descriptor calculation is invalid (it would aggregate properties of disconnected graphs), they will be **excluded** from the training set entirely.
*   **Impact:** This excludes 10 compounds, leaving 7,795 single-component organic compounds intact without modifying their protonation states or stripping fragments.

---

## 4. Duplicate Structural Analysis

A duplicate inspection was run on the raw B3DB classification dataset:
*   **Raw SMILES duplicates:** 0
*   **Canonical SMILES duplicates:** 0
*   *Conclusion:* The dataset curators have already performed structural deduplication. There are no duplicate structures or conflicting labels in terms of identical canonical SMILES strings.
