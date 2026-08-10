import os
import sys
import json
import time
import joblib
import pandas as pd
from rdkit import Chem
from sklearn.ensemble import RandomForestClassifier

# Ensure backend folder is in path for modules import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Paths
CLEANED_DATA_PATH = "backend/data/processed/b3db_cleaned.csv"
DESCRIPTORS_PATH = "features/descriptors.csv"
MODELS_DIR = "backend/models"

FEATURE_ORDER = [
    "Molecular Weight",
    "LogP",
    "TPSA",
    "H-Bond Donors",
    "H-Bond Acceptors",
    "Rotatable Bonds",
    "Ring Count",
    "Aromatic Ring Count",
    "Heavy Atom Count",
    "Fraction CSP3",
    "Formal Charge"
]

FEATURE_DESCRIPTIONS = {
    "Molecular Weight": "Molecular weight (bulk mass indicator)",
    "LogP": "Wildman-Crippen partition coefficient (lipophilicity)",
    "TPSA": "Topological polar surface area (molecular polarity)",
    "H-Bond Donors": "Number of hydrogen-bond donors",
    "H-Bond Acceptors": "Number of hydrogen-bond acceptors",
    "Rotatable Bonds": "Number of rotatable bonds (conformational flexibility)",
    "Ring Count": "Total number of rings",
    "Aromatic Ring Count": "Number of aromatic rings",
    "Heavy Atom Count": "Count of non-hydrogen atoms",
    "Fraction CSP3": "Fraction of sp3 hybridized carbons (saturation index)",
    "Formal Charge": "Net formal charge of the molecule"
}

def main():
    print("--- Phase 6: Production Model Retraining ---")
    
    # 1. Load data
    if not os.path.exists(CLEANED_DATA_PATH):
        print(f"ERROR: Cleaned data not found at {CLEANED_DATA_PATH}")
        return
    if not os.path.exists(DESCRIPTORS_PATH):
        print(f"ERROR: Descriptors matrix not found at {DESCRIPTORS_PATH}")
        return
        
    df = pd.read_csv(CLEANED_DATA_PATH)
    desc_df = pd.read_csv(DESCRIPTORS_PATH, index_col=0)
    
    # Encode target: BBB+ -> 1, BBB- -> 0
    y = (df["BBB+/BBB-"] == "BBB+").astype(int).values
    
    # Align and order descriptors
    X = desc_df[FEATURE_ORDER].values
    
    print(f"Training set loaded: {X.shape[0]} samples, {X.shape[1]} descriptors.")
    
    # Ensure models directory exists
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        
    # 2. Retrain selected architecture
    # Parameters match Phase 4/5 baseline
    rf_params = {
        "n_estimators": 250,
        "max_depth": 12,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "max_features": "sqrt",
        "class_weight": "balanced",
        "random_state": 42
    }
    
    print("Retraining selected Random Forest model on ALL 7,795 molecules...")
    start_time = time.time()
    
    model = RandomForestClassifier(**rf_params)
    model.fit(X, y)
    
    duration = time.time() - start_time
    print(f"Model retrained successfully in {duration:.2f} seconds.")
    
    # 3. Serialize Model
    model_path = os.path.join(MODELS_DIR, "production_model.joblib")
    joblib.dump(model, model_path)
    print(f"Production model serialized to: {model_path}")
    
    # 4. Generate metadata
    metadata = {
        "model_type": "RandomForestClassifier",
        "model_version": "1.0.0",
        "training_dataset_name": "b3db_cleaned.csv",
        "training_sample_count": int(X.shape[0]),
        "feature_names": FEATURE_ORDER,
        "feature_descriptions": FEATURE_DESCRIPTIONS,
        "target_mapping": {
            "BBB+": 1,
            "BBB-": 0
        },
        "hyperparameters": rf_params,
        "training_duration_seconds": duration,
        "training_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment_versions": {
            "scikit_learn": __import__('sklearn').__version__,
            "rdkit": __import__('rdkit').__version__,
            "python": sys.version
        },
        "evaluation_benchmark": {
            "source_reference": "Phase 5 Bemis-Murcko scaffold-split evaluation model",
            "metrics": {
                "accuracy": 0.7447,
                "macro_f1": 0.7212,
                "roc_auc": 0.8017,
                "pr_auc": 0.8504
            },
            "note": "Evaluation metrics belong to the scaffold-split model. No independent test metric is claimed for this retrained production model."
        }
    }
    
    meta_path = os.path.join(MODELS_DIR, "production_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Production metadata written to: {meta_path}")

if __name__ == "__main__":
    main()
