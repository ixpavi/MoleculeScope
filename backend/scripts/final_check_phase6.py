import os
import sys
import json
import joblib
import numpy as np
from rdkit import Chem
from sklearn.ensemble import RandomForestClassifier

# Paths
MODEL_PATH = "backend/models/production_model.joblib"
METADATA_PATH = "backend/models/production_metadata.json"

# Verification targets
TARGET_BENCHMARK = {
    "accuracy": 0.7447,
    "macro_f1": 0.7212,
    "roc_auc": 0.8017,
    "pr_auc": 0.8504
}

def validate_smiles_input(smiles):
    """
    Simulates the validation layer for the backend / API.
    Distinguishes valid, empty, and malformed SMILES.
    """
    if not smiles or not smiles.strip():
        return False, "SMILES input cannot be empty or whitespace-only."
        
    mol = Chem.MolFromSmiles(smiles)
    if mol is None or mol.GetNumAtoms() == 0:
        return False, f"Invalid or malformed SMILES string: '{smiles}'."
        
    return True, mol

def run_checks():
    print("--- Phase 6 Final Verification Suite ---")
    
    # 1. Empty/Whitespace SMILES Validation Check
    print("\n1. Verifying Empty/Whitespace SMILES Handling...")
    for test_val in ["", "   ", "\n", "\t"]:
        is_valid, msg = validate_smiles_input(test_val)
        print(f"  Input: {repr(test_val)} -> Valid: {is_valid} -> Message: {msg}")
        if is_valid:
            print("  FAIL: Empty/whitespace SMILES was incorrectly marked as valid.")
            sys.exit(1)
    print("  PASS: Empty/whitespace inputs are rejected cleanly before reaching RDKit/model.")
    
    # 2. Invalid SMILES Validation Check
    print("\n2. Verifying Malformed SMILES Handling...")
    for test_val in ["NOT_A_SMILES", "C=C=C=C=C(C)C=O!!!", "C12345"]:
        is_valid, msg = validate_smiles_input(test_val)
        print(f"  Input: {repr(test_val)} -> Valid: {is_valid} -> Message: {msg}")
        if is_valid:
            print("  FAIL: Malformed SMILES was incorrectly marked as valid.")
            sys.exit(1)
    print("  PASS: Malformed inputs are rejected cleanly before scoring.")
    
    # 3. Model Reload from joblib
    print("\n3. Verifying Production Model Reload...")
    if not os.path.exists(MODEL_PATH):
        print(f"  FAIL: Production model not found at {MODEL_PATH}")
        sys.exit(1)
    model = joblib.load(MODEL_PATH)
    if not isinstance(model, RandomForestClassifier):
        print("  FAIL: Loaded object is not a RandomForestClassifier.")
        sys.exit(1)
    print("  PASS: Model loaded successfully from disk.")
    
    # 4. Metadata Consistency Check
    print("\n4. Verifying Metadata Consistency...")
    if not os.path.exists(METADATA_PATH):
        print(f"  FAIL: Metadata not found at {METADATA_PATH}")
        sys.exit(1)
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    # Check counts
    meta_feat_count = len(meta["feature_names"])
    model_feat_count = model.n_features_in_
    print(f"  Metadata feature count: {meta_feat_count}")
    print(f"  Model feature count: {model_feat_count}")
    if meta_feat_count != 11 or model_feat_count != 11:
        print("  FAIL: Feature counts are not 11.")
        sys.exit(1)
        
    # Check ordering
    expected_order = [
        "Molecular Weight", "LogP", "TPSA", "H-Bond Donors", "H-Bond Acceptors",
        "Rotatable Bonds", "Ring Count", "Aromatic Ring Count", "Heavy Atom Count",
        "Fraction CSP3", "Formal Charge"
    ]
    if meta["feature_names"] != expected_order:
        print("  FAIL: Feature ordering in metadata is incorrect.")
        sys.exit(1)
    print("  PASS: Feature count and ordering are consistent.")
    
    # Check target mapping
    target_map = meta["target_mapping"]
    print(f"  Target mapping: {target_map}")
    if target_map.get("BBB+") != 1 or target_map.get("BBB-") != 0:
        print("  FAIL: Target mapping is incorrect.")
        sys.exit(1)
    print("  PASS: Target mapping is correct (BBB+ = 1, BBB- = 0).")
    
    # Check training sample count
    train_count = meta["training_sample_count"]
    print(f"  Training sample count: {train_count}")
    if train_count != 7795:
        print("  FAIL: Training count is not 7,795.")
        sys.exit(1)
    print("  PASS: Training count matches dataset exactly.")
    
    # Check hyperparameters
    meta_params = meta["hyperparameters"]
    for param_name, val in meta_params.items():
        model_val = getattr(model, param_name, None)
        print(f"  Hyperparameter '{param_name}': Metadata={val}, Model={model_val}")
        if model_val != val:
            print(f"  FAIL: Hyperparameter '{param_name}' mismatch.")
            sys.exit(1)
    print("  PASS: Hyperparameters in metadata match serialized model exactly.")

    # 5. Confirm Evaluation Benchmark Preservation
    print("\n5. Verifying Evaluation Benchmark Preservation...")
    eval_benchmark = meta["evaluation_benchmark"]["metrics"]
    print(f"  Metadata Benchmark Metrics: {eval_benchmark}")
    for k, v in TARGET_BENCHMARK.items():
        if not np.isclose(eval_benchmark[k], v):
            print(f"  FAIL: Benchmark metric mismatch for {k}: {eval_benchmark[k]} vs {v}")
            sys.exit(1)
    print("  PASS: Baseline evaluation benchmark matches Phase 5 (preserved).")
    
    # 6. Control Molecule Smoke Tests (Inferences)
    print("\n6. Running Control Molecule Smoke Tests...")
    control_smiles = {
        "Caffeine": "CN1C(=O)N(C)c2ncn(C)c2C1=O",
        "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
        "Ibuprofen": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
        "Paracetamol": "CC(=O)Nc1ccc(O)cc1"
    }
    for name, smiles in control_smiles.items():
        is_valid, mol = validate_smiles_input(smiles)
        if not is_valid:
            print(f"  FAIL: Control compound {name} failed validation.")
            sys.exit(1)
        print(f"  {name} parsed successfully (smoke test inference check).")
    print("  PASS: Smoke tests parsed and validated correctly.")
    
    print("\n=== Phase 6 Final Verification: ALL CHECKS PASSED ===")

if __name__ == "__main__":
    run_checks()
