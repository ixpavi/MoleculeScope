import os
import sys
import json
import joblib
import numpy as np
from rdkit import Chem
from sklearn.ensemble import RandomForestClassifier

# Add backend and project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.features.descriptors import compute_single_descriptors, get_descriptor_names

# Paths
MODEL_PATH = "backend/models/production_model.joblib"
METADATA_PATH = "backend/models/production_metadata.json"

FEATURE_ORDER = get_descriptor_names()

# Control compounds
CONTROL_MOLECULES = {
    "Caffeine": "CN1C(=O)N(C)c2ncn(C)c2C1=O",
    "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "Ibuprofen": "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
    "Paracetamol": "CC(=O)Nc1ccc(O)cc1"
}

def verify_pipeline():
    print("=== Production Model Verification Suite ===")
    
    # --- A. Model Loading ---
    print("\n[A] Verifying Model Loading...")
    if not os.path.exists(MODEL_PATH):
        print(f"FAIL: Model file not found at {MODEL_PATH}")
        sys.exit(1)
        
    model = joblib.load(MODEL_PATH)
    if not isinstance(model, RandomForestClassifier):
        print(f"FAIL: Loaded object is type {type(model)}, expected RandomForestClassifier.")
        sys.exit(1)
    print("PASS: Model loaded successfully and is a RandomForestClassifier.")
    
    # --- B. Feature Compatibility & Metadata ---
    print("\n[B] Verifying Feature Compatibility & Metadata...")
    if not os.path.exists(METADATA_PATH):
        print(f"FAIL: Metadata file not found at {METADATA_PATH}")
        sys.exit(1)
        
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    # Check feature count
    if len(meta["feature_names"]) != 11:
        print(f"FAIL: Metadata lists {len(meta['feature_names'])} features, expected 11.")
        sys.exit(1)
        
    # Check feature ordering
    if meta["feature_names"] != FEATURE_ORDER:
        print("FAIL: Feature ordering in metadata does not match FEATURE_ORDER mapping.")
        sys.exit(1)
        
    if model.n_features_in_ != 11:
        print(f"FAIL: Model expects {model.n_features_in_} features, expected 11.")
        sys.exit(1)
        
    print("PASS: Feature count, ordering, and metadata match expectations.")
    print(f"Features: {meta['feature_names']}")

    # --- C. Control Molecule Inference ---
    print("\n[C] Verifying Control Molecule Inference...")
    inferences = {}
    for name, smiles in CONTROL_MOLECULES.items():
        print(f"  Testing {name} (SMILES: {smiles})...")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"FAIL: RDKit could not parse SMILES for {name}")
            sys.exit(1)
            
        desc_dict = compute_single_descriptors(mol)
        
        # Verify all descriptors are present and numeric
        feature_vector = []
        for feat in FEATURE_ORDER:
            val = desc_dict.get(feat)
            if val is None or np.isnan(val) or np.isinf(val):
                print(f"FAIL: Descriptor {feat} for {name} is invalid: {val}")
                sys.exit(1)
            feature_vector.append(val)
            
        # Run inference
        X_test = np.array([feature_vector])
        pred = model.predict(X_test)[0]
        prob = model.predict_proba(X_test)[0]
        
        # Validation checks
        if pred not in [0, 1]:
            print(f"FAIL: Predicted class {pred} is not 0 or 1.")
            sys.exit(1)
            
        if not (0.0 <= prob[1] <= 1.0):
            print(f"FAIL: Probability {prob[1]} is out of [0, 1] range.")
            sys.exit(1)
            
        label = "BBB+" if pred == 1 else "BBB-"
        prob_bbb_plus = prob[1]
        
        print(f"    Descriptors calculated: {feature_vector}")
        print(f"    Prediction: {label} (Predicted probability of BBB+: {prob_bbb_plus:.4f})")
        
        inferences[name] = {
            "descriptors": feature_vector,
            "prediction": label,
            "probability_bbb_plus": prob_bbb_plus
        }
    print("PASS: Inference on control molecules completed successfully without errors.")

    # --- D. Determinism ---
    print("\n[D] Verifying Determinism...")
    caffeine_smiles = CONTROL_MOLECULES["Caffeine"]
    caffeine_mol = Chem.MolFromSmiles(caffeine_smiles)
    caffeine_feats = [compute_single_descriptors(caffeine_mol)[f] for f in FEATURE_ORDER]
    
    first_pred = model.predict(np.array([caffeine_feats]))[0]
    first_prob = model.predict_proba(np.array([caffeine_feats]))[0][1]
    
    for i in range(10):
        # Repeat inference 10 times
        run_pred = model.predict(np.array([caffeine_feats]))[0]
        run_prob = model.predict_proba(np.array([caffeine_feats]))[0][1]
        
        if run_pred != first_pred or not np.isclose(run_prob, first_prob):
            print(f"FAIL: Non-deterministic prediction observed on run {i}")
            sys.exit(1)
            
    print("PASS: Determinism test passed (10 identical runs).")

    # --- E. Invalid SMILES ---
    print("\n[E] Verifying Invalid SMILES Handling...")
    invalid_smiles = "NOT_A_SMILES_STRING!!!!"
    mol_invalid = Chem.MolFromSmiles(invalid_smiles)
    if mol_invalid is None:
        print("  RDKit correctly returned None for invalid SMILES.")
        desc_dict = compute_single_descriptors(mol_invalid)
        if all(val is None for val in desc_dict.values()):
            print("  Pipeline correctly returned None values for all descriptors.")
            # Verify clean validation handling in our script
            print("PASS: Invalid SMILES handled gracefully without crashes.")
        else:
            print("FAIL: Pipeline returned non-None values for invalid SMILES.")
            sys.exit(1)
    else:
        print("FAIL: RDKit parsed an invalid SMILES string.")
        sys.exit(1)

    # --- F. Empty Input ---
    print("\n[F] Verifying Empty Input Handling...")
    empty_smiles = ""
    mol_empty = Chem.MolFromSmiles(empty_smiles)
    if mol_empty is None or mol_empty.GetNumAtoms() == 0:
        print("  RDKit returned None or empty molecule (0 atoms) for empty SMILES.")
        desc_dict = compute_single_descriptors(mol_empty)
        if all(val is None for val in desc_dict.values()):
            print("  Pipeline correctly returned None values for empty SMILES.")
            print("PASS: Empty input handled gracefully without crashes.")
        else:
            print("FAIL: Pipeline returned non-None values for empty SMILES.")
            sys.exit(1)
    else:
        print(f"FAIL: RDKit parsed a molecule with {mol_empty.GetNumAtoms()} atoms for empty SMILES.")
        sys.exit(1)

    print("\n=== Verification Suite Completed: ALL TESTS PASSED ===")
    
    # Return inferences for reporting
    return inferences

if __name__ == "__main__":
    inferences = verify_pipeline()
    
    # Save test outputs to json file for documentation
    output_path = "backend/models/verification_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inferences, f, indent=2)
    print(f"\nVerification results saved to: {output_path}")
