import os
import pandas as pd
import requests
from rdkit import Chem

DATASET_URL = "https://raw.githubusercontent.com/theochem/B3DB/master/B3DB/B3DB_classification.tsv"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RAW_PATH = os.path.join(DATA_DIR, "B3DB_classification_raw.tsv")

def main():
    print("--- Phase 0: Obtaining and Inspecting B3DB ---")
    
    # 1. Ensure directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    # 2. Download raw file if not present
    if not os.path.exists(RAW_PATH):
        print(f"Downloading B3DB from: {DATASET_URL}")
        try:
            response = requests.get(DATASET_URL)
            response.raise_for_status()
            with open(RAW_PATH, "w", encoding="utf-8") as f:
                f.write(response.text)
            print("Download complete.")
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return
    else:
        print(f"Dataset already exists locally at: {RAW_PATH}")
        
    # 3. Load dataset
    df = pd.read_csv(RAW_PATH, sep="\t")
    print(f"\n[Raw Stats]")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {df.columns.tolist()}")
    
    # 4. Column existence verification
    smiles_col = "SMILES"
    target_col = "BBB+/BBB-"
    
    if smiles_col not in df.columns:
        print(f"ERROR: SMILES column '{smiles_col}' not found!")
        return
    if target_col not in df.columns:
        print(f"ERROR: Target column '{target_col}' not found!")
        return
        
    print(f"  Verified columns '{smiles_col}' and '{target_col}' exist.")
    
    # 5. Missing values in raw columns
    missing_smiles = df[smiles_col].isna().sum()
    missing_target = df[target_col].isna().sum()
    print(f"\n[Missing Values]")
    print(f"  Missing SMILES: {missing_smiles}")
    print(f"  Missing target labels: {missing_target}")
    
    # 6. Raw Class distribution
    class_counts = df[target_col].value_counts(dropna=False)
    print(f"\n[Raw Class Distribution]")
    for cls, count in class_counts.items():
        pct = (count / len(df)) * 100
        print(f"    {cls}: {count} ({pct:.2f}%)")
        
    # 7. RDKit validation & Salt/multi-component detection
    print("\n[RDKit Structural Analysis]")
    print("  Validating SMILES strings with RDKit...")
    invalid_count = 0
    multi_component_count = 0
    canonical_smiles_list = []
    
    for idx, row in df.iterrows():
        s = row[smiles_col]
        if pd.isna(s) or not isinstance(s, str):
            invalid_count += 1
            canonical_smiles_list.append(None)
            continue
            
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            invalid_count += 1
            canonical_smiles_list.append(None)
        else:
            # Check if SMILES contains '.' (dot-disconnected components)
            if "." in s:
                multi_component_count += 1
            
            # Canonicalize structures
            canon = Chem.MolToSmiles(mol, canonical=True)
            canonical_smiles_list.append(canon)
            
    df["canonical_smiles"] = canonical_smiles_list
    print(f"  Total invalid SMILES: {invalid_count}")
    print(f"  Total dot-disconnected/multi-component structures: {multi_component_count}")
    
    # Let's inspect some of the dot-disconnected SMILES
    if multi_component_count > 0:
        print("\n  Sample multi-component structures:")
        multi_mols = df[df[smiles_col].str.contains(r"\.", na=False, regex=True)].head(5)
        for idx, row in multi_mols.iterrows():
            print(f"    Name: {row.get('compound_name', 'N/A')} | SMILES: {row[smiles_col]} | Label: {row[target_col]}")
            
    # 8. Duplicate structures duplicate analysis
    print("\n[Duplicate Structure Analysis]")
    valid_df = df[df["canonical_smiles"].notna()].copy()
    
    dup_mask = valid_df.duplicated(subset=["canonical_smiles"], keep=False)
    dup_df = valid_df[dup_mask]
    unique_dups = dup_df["canonical_smiles"].nunique()
    total_dup_rows = len(dup_df)
    print(f"  Total rows that represent duplicate structures: {total_dup_rows}")
    print(f"  Number of unique structures duplicated: {unique_dups}")
    
    # Conflict analysis
    conflicting_dups = 0
    agreed_dups = 0
    conflicting_examples = []
    
    for canon, group in dup_df.groupby("canonical_smiles"):
        labels = group[target_col].unique()
        if len(labels) > 1:
            conflicting_dups += 1
            conflicting_examples.append({
                "smiles": canon,
                "names": group["compound_name"].tolist(),
                "labels": group[target_col].tolist(),
                "groups": group["group"].tolist(),
                "references": group["reference"].tolist()
            })
        else:
            agreed_dups += 1
            
    print(f"  Duplicates with agreed labels: {agreed_dups}")
    print(f"  Duplicates with conflicting labels: {conflicting_dups}")
    
    if conflicting_dups > 0:
        print("\n  Sample conflicting label duplicate cases:")
        for case in conflicting_examples[:5]:
            print(f"    SMILES: {case['smiles']}")
            print(f"      Names: {case['names']}")
            print(f"      Labels: {case['labels']}")
            print(f"      Confidence Groups: {case['groups']}")
            print(f"      References: {case['references']}")
            
    print("\n--- Phase 0 Inspection Complete ---")

if __name__ == "__main__":
    main()
