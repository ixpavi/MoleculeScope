import os
import pandas as pd
from rdkit import Chem
from rdkit import RDLogger

# Disable RDKit logging temporarily to capture stdout/stderr programmatically if needed
# or keep it enabled to see standard errors.
RAW_PATH = "backend/data/B3DB_classification_raw.tsv"

def check_invalid(df):
    print("=== INVALID SMILES DETAILS ===")
    invalid_indices = []
    for idx, row in df.iterrows():
        s = row["SMILES"]
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            invalid_indices.append(idx)
            print(f"Index: {idx} | Name: {row['compound_name']} | Label: {row['BBB+/BBB-']}")
            print(f"  SMILES: {s}")
            # Try to compile and print the exact RDKit validation error
            # RDKit outputs validation errors to stderr by default
            print("  RDKit Parsing: FAILED")
            print("-" * 50)
    return invalid_indices

def check_dot_disconnected(df):
    print("=== DOT-DISCONNECTED SMILES DETAILS ===")
    dot_df = df[df["SMILES"].str.contains(r"\.", na=False, regex=True)]
    print(f"Total multi-component structures: {len(dot_df)}\n")
    for idx, row in dot_df.iterrows():
        s = row["SMILES"]
        mol = Chem.MolFromSmiles(s)
        parsed = "YES" if mol is not None else "NO"
        parts = s.split(".")
        print(f"Index: {idx} | Name: {row['compound_name']} | Label: {row['BBB+/BBB-']}")
        print(f"  SMILES: {s}")
        print(f"  Components: {len(parts)} | RDKit Parsable: {parsed}")
        if mol is not None:
            canonical = Chem.MolToSmiles(mol, canonical=True)
            print(f"  Canonical representation: {canonical}")
        print("-" * 50)

def main():
    if not os.path.exists(RAW_PATH):
        print(f"Error: {RAW_PATH} not found.")
        return
    df = pd.read_csv(RAW_PATH, sep="\t")
    check_invalid(df)
    check_dot_disconnected(df)

if __name__ == "__main__":
    main()
