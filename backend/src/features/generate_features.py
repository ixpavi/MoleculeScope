import os
import sys
import json
import time
import numpy as np
import pandas as pd
from rdkit import Chem

# Ensure backend folder is in path for modules import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.descriptors import compute_descriptors_dataframe, get_descriptor_names, compute_single_descriptors
from features.fingerprints import compute_fingerprints_matrix, compute_single_morgan_fingerprint
from features.feature_checks import run_descriptor_checks, run_fingerprint_checks, verify_fingerprint_determinism

CLEANED_DATA_PATH = "backend/data/processed/b3db_cleaned.csv"
FEATURES_DIR = "features"

# Example molecules for sanity check verification
EXAMPLE_MOLECULES = [
    {"name": "Caffeine", "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"},
    {"name": "Aspirin", "smiles": "CC(=O)Oc1ccccc1C(=O)O"},
    {"name": "Ibuprofen", "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O"},
    {"name": "Paracetamol", "smiles": "CC(=O)Nc1ccc(O)cc1"}
]

def main():
    print("--- Phase 2: Molecular Feature Engineering ---")
    
    # 1. Load cleaned dataset
    if not os.path.exists(CLEANED_DATA_PATH):
        print(f"ERROR: Cleaned dataset not found at: {CLEANED_DATA_PATH}")
        return
        
    df = pd.read_csv(CLEANED_DATA_PATH)
    num_mols = len(df)
    print(f"Loaded cleaned dataset with {num_mols} molecules.")
    
    # Ensure features directory exists
    if not os.path.exists(FEATURES_DIR):
        os.makedirs(FEATURES_DIR)
        
    # 2. Descriptor Generation
    print("Generating molecular descriptors...")
    start_time = time.time()
    desc_df = compute_descriptors_dataframe(df, smiles_col="SMILES")
    desc_time = time.time() - start_time
    print(f"Descriptors generated in {desc_time:.2f}s. Shape: {desc_df.shape}")
    
    # Save descriptors to CSV
    desc_path = os.path.join(FEATURES_DIR, "descriptors.csv")
    desc_df.to_csv(desc_path, index=True)
    print(f"Saved descriptors to: {desc_path}")
    
    # 3. Fingerprint Generation
    print("Generating Morgan fingerprints (radius=2, nBits=2048)...")
    start_time = time.time()
    fp_matrix = compute_fingerprints_matrix(df, smiles_col="SMILES")
    fp_time = time.time() - start_time
    print(f"Fingerprints generated in {fp_time:.2f}s. Shape: {fp_matrix.shape}")
    
    # Save fingerprints as NPZ
    fp_path = os.path.join(FEATURES_DIR, "fingerprints.npz")
    np.savez_compressed(fp_path, fingerprints=fp_matrix)
    print(f"Saved fingerprints to: {fp_path}")
    
    # 4. Combined Representation (Concatenation)
    print("Creating combined feature matrix...")
    desc_arr = desc_df.values
    combined_matrix = np.hstack((desc_arr, fp_matrix))
    print(f"Combined feature matrix shape: {combined_matrix.shape}")
    
    # Save combined as NPZ
    combined_path = os.path.join(FEATURES_DIR, "combined.npz")
    np.savez_compressed(combined_path, combined=combined_matrix)
    print(f"Saved combined features to: {combined_path}")
    
    # 5. Run Quality Control Checks
    print("\nRunning QC Checks...")
    desc_qc = run_descriptor_checks(desc_df)
    fp_qc = run_fingerprint_checks(fp_matrix)
    deterministic = verify_fingerprint_determinism()
    
    print(f"  Descriptors constant features count: {len(desc_qc['constant_features'])}")
    print(f"  Descriptors highly correlated pairs (r >= 0.90) count: {len(desc_qc['high_correlation_pairs'])}")
    print(f"  Fingerprints avg active bits: {fp_qc['mean_active_bits']:.2f}")
    print(f"  Fingerprints min active bits: {fp_qc['min_active_bits']}")
    print(f"  Fingerprints max active bits: {fp_qc['max_active_bits']}")
    print(f"  Fingerprints determinism check: {'PASSED' if deterministic else 'FAILED'}")
    
    # 6. Sanity check example molecules
    print("\n--- Example Molecule Sanity Checks (Verification Only) ---")
    sanity_checks = []
    for mol_info in EXAMPLE_MOLECULES:
        name = mol_info["name"]
        raw_s = mol_info["smiles"]
        mol = Chem.MolFromSmiles(raw_s)
        canon_s = Chem.MolToSmiles(mol, canonical=True)
        
        # Descriptors
        desc_dict = compute_single_descriptors(mol)
        
        # Fingerprints
        fp_arr = compute_single_morgan_fingerprint(mol)
        active_bits = int(fp_arr.sum()) if fp_arr is not None else 0
        
        print(f"Compound: {name}")
        print(f"  Raw SMILES:       {raw_s}")
        print(f"  Canonical SMILES: {canon_s}")
        print(f"  MW:               {desc_dict['Molecular Weight']:.2f}")
        print(f"  LogP:             {desc_dict['LogP']:.2f}")
        print(f"  TPSA:             {desc_dict['TPSA']:.2f}")
        print(f"  Fingerprint bits: {len(fp_arr) if fp_arr is not None else 0}")
        print(f"  Active bits count: {active_bits}")
        print("-" * 50)
        
        sanity_checks.append({
            "name": name,
            "raw_smiles": raw_s,
            "canonical_smiles": canon_s,
            "descriptors": desc_dict,
            "fp_len": len(fp_arr) if fp_arr is not None else 0,
            "active_bits": active_bits
        })
        
    # 7. Write Machine-Readable Metadata (JSON)
    metadata = {
        "dataset_source": "B3DB Classification (theochem/B3DB)",
        "num_molecules_processed": num_mols,
        "descriptor_names": get_descriptor_names(),
        "descriptor_count": len(get_descriptor_names()),
        "fingerprint_settings": {
            "type": "Morgan Circular Fingerprint (ECFP4 equivalent)",
            "radius": 2,
            "nBits": 2048,
            "use_chirality": False,
            "output_type": "binary (int8 bit vector)"
        },
        "combined_feature_count": combined_matrix.shape[1],
        "rdkit_version": __import__('rdkit').__version__,
        "python_version": sys.version,
        "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "output_files": {
            "descriptors": desc_path,
            "fingerprints": fp_path,
            "combined": combined_path
        },
        "quality_control_summary": {
            "descriptor_constant_features": desc_qc["constant_features"],
            "descriptor_high_correlation_pairs": desc_qc["high_correlation_pairs"],
            "fingerprint_stats": fp_qc,
            "fingerprint_determinism_verified": deterministic
        }
    }
    
    meta_path = os.path.join(FEATURES_DIR, "feature_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved feature metadata to: {meta_path}")
    
    # 8. Write Human-Readable Feature Summary Markdown
    write_summary_md(num_mols, desc_df, desc_qc, fp_qc, deterministic, combined_matrix.shape[1], sanity_checks)

def write_summary_md(num_mols, desc_df, desc_qc, fp_qc, deterministic, combined_dim, sanity_checks):
    summary_path = os.path.join(FEATURES_DIR, "feature_summary.md")
    
    # Format highly correlated pairs
    corr_rows = ""
    for pair in desc_qc["high_correlation_pairs"]:
        corr_rows += f"| {pair['feature_1']} | {pair['feature_2']} | {pair['correlation']:.4f} |\n"
        
    if not corr_rows:
        corr_rows = "| None | None | N/A |\n"
        
    # Format descriptor ranges
    desc_rows = ""
    for desc_name, stats in desc_qc["descriptor_stats"].items():
        desc_rows += f"| {desc_name} | {stats['nan_count']} | {stats['inf_count']} | {stats['min']:.2f} | {stats['max']:.2f} | {stats['mean']:.2f} | {stats['median']:.2f} | {stats['std']:.2f} | {stats['constant']} |\n"
        
    # Format sanity checks
    sanity_block = ""
    for s in sanity_checks:
        sanity_block += f"### {s['name']}\n"
        sanity_block += f"*   **Raw SMILES:** `{s['raw_smiles']}`\n"
        sanity_block += f"*   **Canonical SMILES:** `{s['canonical_smiles']}`\n"
        sanity_block += f"*   **Fingerprint Bits Count:** {s['fp_len']} (Active: {s['active_bits']})\n"
        sanity_block += "*   **Descriptors:**\n"
        for name, val in s["descriptors"].items():
            sanity_block += f"    *   {name}: `{val:.4f}`\n"
        sanity_block += "\n"
        
    markdown_content = f"""# Feature Engineering Summary — MoleculeScope

This document records the molecular feature generation results and quality control metrics for Phase 2.

---

## 1. Feature Dimensions Summary

*   **Total Molecules Processed:** {num_mols}
*   **Representation A (Descriptors):** {desc_df.shape[1]} features (recorded in `descriptors.csv`)
*   **Representation B (Fingerprints):** {fp_qc['total_bits_per_molecule']} binary bits (recorded in `fingerprints.npz`)
*   **Representation C (Combined):** {combined_dim} features (recorded in `combined.npz`)

---

## 2. Molecular Descriptors Statistics & Ranges

| Descriptor | NaN Count | Inf Count | Min | Max | Mean | Median | Std | Constant? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{desc_rows}

---

## 3. Descriptor Correlation Analysis

High correlation ($r \\ge 0.90$) identified between the following descriptors:

| Feature 1 | Feature 2 | Correlation ($r$) |
| :--- | :--- | :--- |
{corr_rows}

*Note:* These correlated descriptors are preserved in the raw feature matrix. Collinearity will be handled inside model-specific pipelines later (e.g., L2 regularization in Logistic Regression or tree-splitting in RF/XGBoost).

---

## 4. Morgan Fingerprints Quality Control

*   **Fingerprint Type:** Morgan Circular Fingerprint (ECFP4 equivalent)
*   **Radius:** 2 (Diameter = 4)
*   **Bit Count (`nBits`):** 2048
*   **Chirality Included:** False
*   **Output representation:** Binary bit vector (`int8`)
*   **NaN / Inf Counts:** {fp_qc['nan_count']} / {fp_qc['inf_count']}
*   **Active Bits statistics:**
    *   Minimum active bits: {fp_qc['min_active_bits']}
    *   Maximum active bits: {fp_qc['max_active_bits']}
    *   Mean active bits: {fp_qc['mean_active_bits']:.2f} ({fp_qc['average_density_pct']:.2f}% density)
    *   Median active bits: {fp_qc['median_active_bits']:.2f}
*   **Determinism Verified:** {'YES' if deterministic else 'NO'} (confirmed identical output vectors across separate iterations)

---

## 5. Example Molecules Sanity Checks

All molecular property calculations are executed dynamically in RDKit.

{sanity_block}
"""
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Human-readable feature summary written to: {summary_path}")

if __name__ == "__main__":
    main()
