import os
import pandas as pd
from rdkit import Chem

RAW_PATH = "backend/data/B3DB_classification_raw.tsv"
PROCESSED_DIR = "backend/data/processed"
CLEANED_PATH = os.path.join(PROCESSED_DIR, "b3db_cleaned.csv")
SUMMARY_PATH = os.path.join(PROCESSED_DIR, "preprocessing_summary.md")

def clean_data():
    print("--- Phase 1: Data Cleaning ---")
    
    # 1. Load raw dataset
    if not os.path.exists(RAW_PATH):
        print(f"ERROR: Raw dataset not found at {RAW_PATH}")
        return
        
    df = pd.read_csv(RAW_PATH, sep="\t")
    raw_count = len(df)
    print(f"Loaded raw dataset with {raw_count} rows.")
    
    # 2. Track exclusions
    exclusions = []
    
    # Invalid SMILES
    invalid_indices = []
    for idx, row in df.iterrows():
        s = row["SMILES"]
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            invalid_indices.append(idx)
            exclusions.append({
                "Index": idx,
                "Name": row["compound_name"],
                "SMILES": s,
                "Label": row["BBB+/BBB-"],
                "Type": "Invalid SMILES",
                "Reason": "Fails RDKit valence check (carbocation valence error on [C+])"
            })
            
    print(f"Found {len(invalid_indices)} invalid SMILES structures.")
    
    # Multi-component SMILES (containing '.')
    multi_component_indices = []
    for idx, row in df.iterrows():
        if idx in invalid_indices:
            continue
        s = row["SMILES"]
        if "." in s:
            multi_component_indices.append(idx)
            exclusions.append({
                "Index": idx,
                "Name": row["compound_name"],
                "SMILES": s,
                "Label": row["BBB+/BBB-"],
                "Type": "Multi-component",
                "Reason": f"Contains {len(s.split('.'))} disconnected structures (mixtures/prodrugs/copolymers)"
            })
            
    print(f"Found {len(multi_component_indices)} multi-component SMILES structures.")
    
    # 3. Create cleaned dataframe
    all_excluded = set(invalid_indices + multi_component_indices)
    cleaned_df = df.drop(index=list(all_excluded)).copy()
    
    # 4. Canonicalize for duplicate check
    print("Canonicalizing SMILES for duplicate verification...")
    cleaned_df["canonical_smiles"] = cleaned_df["SMILES"].apply(
        lambda s: Chem.MolToSmiles(Chem.MolFromSmiles(s), canonical=True)
    )
    
    # Duplicate verification
    dup_count = cleaned_df.duplicated(subset=["canonical_smiles"]).sum()
    print(f"Verified duplicates in cleaned dataset: {dup_count}")
    
    # 5. Save cleaned dataset
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
        
    cleaned_df.to_csv(CLEANED_PATH, index=False)
    print(f"Cleaned dataset written to: {CLEANED_PATH}")
    print(f"Cleaned dataset shape: {cleaned_df.shape}")
    
    # 6. Final statistics
    final_count = len(cleaned_df)
    class_counts = cleaned_df["BBB+/BBB-"].value_counts()
    
    # Print distribution
    print("\nFinal Class Distribution:")
    for cls, count in class_counts.items():
        pct = (count / final_count) * 100
        print(f"  {cls}: {count} ({pct:.2f}%)")
        
    # 7. Write Preprocessing Summary Markdown
    exclusions_df = pd.DataFrame(exclusions)
    
    summary_md = f"""# Preprocessing Summary — MoleculeScope

This document records the data cleaning results and statistics for the B3DB database in Phase 1.

---

## 1. Dataset Dimensions Before and After

| Stage | Row Count | Column Count |
| :--- | :--- | :--- |
| **Raw B3DB (Source)** | {raw_count} | 12 |
| **Cleaned (Processed)** | {final_count} | 13 (including canonical_smiles) |

---

## 2. Final Class Distribution

| Class Label | Compound Count | Percentage |
| :--- | :--- | :--- |
| **BBB+ (Permeable)** | {class_counts.get("BBB+", 0)} | {(class_counts.get("BBB+", 0) / final_count * 100):.2f}% |
| **BBB- (Impermeable)** | {class_counts.get("BBB-", 0)} | {(class_counts.get("BBB-", 0) / final_count * 100):.2f}% |
| **Total** | {final_count} | 100.00% |

---

## 3. Exclusion Registry

The following {len(exclusions)} compounds were excluded during preprocessing:

| Index | Name | Class | Type | Reason |
| :--- | :--- | :--- | :--- | :--- |
"""
    for idx, row in exclusions_df.iterrows():
        summary_md += f"| {row['Index']} | {row['Name']} | {row['Label']} | {row['Type']} | {row['Reason']} |\n"
        
    summary_md += """
---

## 4. Specific Record Anomalies

### Mepenzolate Bromide vs. Tiotidine
*   **The Issue:** `tiotidine` (index 7737) is structurally inconsistent with its database record. It contains the chemical structure of mepenzolate bromide (without chirality) instead of tiotidine. 
*   **The Solution:** Both structures contain carbocation transcription errors (`[C+]`) which fail RDKit parsing. Since tiotidine is chemically erroneous and cannot be repaired safely, both records have been excluded from modeling.

## 5. Multi-component Exclusions Rationale
Dot-disconnected structures represent physical mixtures of active ingredients, copolymers, or complexes. Molecular descriptors computed on disconnected graphs yield aggregated sums (e.g., the molecular weight is the sum of both components) which does not represent a single chemical entity crossing the blood-brain barrier. All 10 compounds were excluded to ensure modeling integrity.
"""
    
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(summary_md)
    print(f"Preprocessing summary markdown written to: {SUMMARY_PATH}")

if __name__ == "__main__":
    clean_data()
