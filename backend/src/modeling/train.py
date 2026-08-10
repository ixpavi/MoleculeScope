import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, precision_recall_curve, auc

# Ensure backend folder is in path for modules import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Paths
CLEANED_DATA_PATH = "backend/data/processed/b3db_cleaned.csv"
DESCRIPTORS_PATH = "features/descriptors.csv"
FINGERPRINTS_PATH = "features/fingerprints.npz"
COMBINED_PATH = "features/combined.npz"

RANDOM_SPLIT_PATH = "splits/random_split_indices.json"
SCAFFOLD_SPLIT_PATH = "splits/scaffold_split_indices.json"

RESULTS_DIR = "results"
MODELS_DIR = os.path.join(RESULTS_DIR, "models")
PREDS_DIR = os.path.join(RESULTS_DIR, "predictions")
METRICS_DIR = os.path.join(RESULTS_DIR, "metrics")
IMPORTANCE_DIR = os.path.join(RESULTS_DIR, "feature_importance")

def ensure_dirs():
    """Creates directory structures for results."""
    for d in [MODELS_DIR, PREDS_DIR, METRICS_DIR, IMPORTANCE_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def calculate_pr_auc(y_true, y_prob):
    """Calculates Area Under Precision-Recall Curve."""
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    return auc(recall, precision)

def compute_metrics(y_true, y_pred, y_prob):
    """Calculates classification performance metrics."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
        "pr_auc": float(calculate_pr_auc(y_true, y_prob))
    }

def main():
    print("--- Phase 4: Offline Model Training ---")
    ensure_dirs()
    
    # 1. Load Cleaned Dataset and Target Labels
    if not os.path.exists(CLEANED_DATA_PATH):
        print(f"ERROR: Cleaned dataset not found at {CLEANED_DATA_PATH}")
        return
        
    df = pd.read_csv(CLEANED_DATA_PATH)
    # Target Encoding: BBB+ = 1, BBB- = 0
    y_all = (df["BBB+/BBB-"] == "BBB+").astype(int).values
    
    # 2. Load Feature Representations
    print("Loading feature representations...")
    desc_df = pd.read_csv(DESCRIPTORS_PATH, index_col=0)
    desc_features = desc_df.columns.tolist()
    X_desc = desc_df.values
    
    with np.load(FINGERPRINTS_PATH) as data:
        X_fp = data["fingerprints"]
        
    with np.load(COMBINED_PATH) as data:
        X_comb = data["combined"]
        
    print(f"  Descriptors: {X_desc.shape}")
    print(f"  Fingerprints: {X_fp.shape}")
    print(f"  Combined:     {X_comb.shape}")
    
    # 3. Load Split Indices
    with open(RANDOM_SPLIT_PATH, "r") as f:
        rand_split = json.load(f)
        
    with open(SCAFFOLD_SPLIT_PATH, "r") as f:
        scaff_split = json.load(f)
        
    splits = {
        "random": {
            "train": rand_split["train_indices"],
            "test": rand_split["test_indices"]
        },
        "scaffold": {
            "train": scaff_split["train_indices"],
            "test": scaff_split["test_indices"]
        }
    }
    
    # 4. Define Baseline Configurations
    # Lock random state = 42 for all models
    models_config = {
        "logistic": {
            "constructor": lambda: LogisticRegression(
                C=0.1, penalty="l2", solver="lbfgs", max_iter=1000, random_state=42
            ),
            "scale_required": {
                "descriptors": "full",
                "fingerprints": "none",
                "combined": "partial" # only first 11 columns
            }
        },
        "rf": {
            "constructor": lambda: RandomForestClassifier(
                n_estimators=250, max_depth=12, min_samples_split=5, min_samples_leaf=2,
                max_features="sqrt", class_weight="balanced", random_state=42
            ),
            "scale_required": {
                "descriptors": "none",
                "fingerprints": "none",
                "combined": "none"
            }
        },
        "xgb": {
            "constructor": lambda: XGBClassifier(
                n_estimators=200, max_depth=6, learning_rate=0.05, subsample=0.8,
                colsample_bytree=0.8, min_child_weight=2, eval_metric="logloss",
                random_state=42
            ),
            "scale_required": {
                "descriptors": "none",
                "fingerprints": "none",
                "combined": "none"
            }
        }
    }
    
    features_config = {
        "descriptors": X_desc,
        "fingerprints": X_fp,
        "combined": X_comb
    }
    
    results_list = []
    
    # 5. Run Baseline Majority Class Classifier (Always Predict BBB+)
    print("\nRunning majority-class baselines (Always predict BBB+)...")
    for split_name, indices in splits.items():
        train_idx = indices["train"]
        test_idx = indices["test"]
        y_test = y_all[test_idx]
        
        # Majority class is BBB+ (encoded as 1)
        majority_preds = np.ones(len(test_idx), dtype=int)
        majority_probs = np.ones(len(test_idx), dtype=float)
        
        maj_metrics = compute_metrics(y_test, majority_preds, majority_probs)
        results_list.append({
            "model": "baseline_majority",
            "representation": "all",
            "split": split_name,
            "train_n": len(train_idx),
            "test_n": len(test_idx),
            "accuracy": maj_metrics["accuracy"],
            "precision": maj_metrics["precision"],
            "recall": maj_metrics["recall"],
            "f1": maj_metrics["f1"],
            "macro_f1": maj_metrics["macro_f1"],
            "roc_auc": maj_metrics["roc_auc"],
            "pr_auc": maj_metrics["pr_auc"]
        })
        print(f"  Majority class baseline on {split_name} split: Accuracy={maj_metrics['accuracy']:.4f}, Macro F1={maj_metrics['macro_f1']:.4f}")
        
    # 6. Run 18 Primary Experiments
    print("\nStarting model training loop...")
    for split_name, indices in splits.items():
        train_idx = indices["train"]
        test_idx = indices["test"]
        
        y_train = y_all[train_idx]
        y_test = y_all[test_idx]
        
        for rep_name, X_full in features_config.items():
            X_train_raw = X_full[train_idx]
            X_test_raw = X_full[test_idx]
            
            for model_name, model_info in models_config.items():
                exp_name = f"{model_name}_{rep_name}_{split_name}"
                print(f"Training: {exp_name}...")
                
                # Preprocessing
                scale_type = model_info["scale_required"][rep_name]
                scaler_obj = None
                
                if scale_type == "full":
                    scaler_obj = StandardScaler()
                    X_train = scaler_obj.fit_transform(X_train_raw)
                    X_test = scaler_obj.transform(X_test_raw)
                elif scale_type == "partial":
                    # Combined representation: scale descriptors (cols 0:11) only, leave fingerprints intact
                    scaler_obj = StandardScaler()
                    X_train = X_train_raw.copy()
                    X_test = X_test_raw.copy()
                    
                    X_train[:, :11] = scaler_obj.fit_transform(X_train_raw[:, :11])
                    X_test[:, :11] = scaler_obj.transform(X_test_raw[:, :11])
                else:
                    X_train = X_train_raw
                    X_test = X_test_raw
                    
                # Fit Model
                model = model_info["constructor"]()
                
                start_time = time.time()
                model.fit(X_train, y_train)
                duration = time.time() - start_time
                
                # Predict
                preds_train = model.predict(X_train)
                preds_test = model.predict(X_test)
                
                # Predict Probability of BBB+ (class 1)
                probs_train = model.predict_proba(X_train)[:, 1]
                probs_test = model.predict_proba(X_test)[:, 1]
                
                # Calculate metrics
                train_metrics = compute_metrics(y_train, preds_train, probs_train)
                test_metrics = compute_metrics(y_test, preds_test, probs_test)
                
                # Record results
                results_list.append({
                    "model": model_name,
                    "representation": rep_name,
                    "split": split_name,
                    "train_n": len(train_idx),
                    "test_n": len(test_idx),
                    "accuracy": test_metrics["accuracy"],
                    "precision": test_metrics["precision"],
                    "recall": test_metrics["recall"],
                    "f1": test_metrics["f1"],
                    "macro_f1": test_metrics["macro_f1"],
                    "roc_auc": test_metrics["roc_auc"],
                    "pr_auc": test_metrics["pr_auc"]
                })
                
                # 7. Save Predictions Artifact
                pred_path = os.path.join(PREDS_DIR, f"{exp_name}_predictions.csv")
                pd.DataFrame({
                    "true_label": y_test,
                    "predicted_label": preds_test,
                    "predicted_prob": probs_test
                }).to_csv(pred_path, index=False)
                
                # 8. Save Metrics Artifact
                metric_path = os.path.join(METRICS_DIR, f"{exp_name}_metrics.json")
                with open(metric_path, "w") as f:
                    json.dump({
                        "experiment": exp_name,
                        "model_type": model_name,
                        "feature_representation": rep_name,
                        "split_type": split_name,
                        "train_n": len(train_idx),
                        "test_n": len(test_idx),
                        "duration_seconds": duration,
                        "train_metrics": train_metrics,
                        "test_metrics": test_metrics,
                        "software_versions": {
                            "scikit_learn": __import__('sklearn').__version__,
                            "xgboost": __import__('xgboost').__version__,
                            "python": sys.version
                        }
                    }, f, indent=2)
                    
                # 9. Save Feature Importance if available (for descriptors only)
                if rep_name == "descriptors":
                    importances = None
                    if hasattr(model, "feature_importances_"):
                        importances = model.feature_importances_
                    elif hasattr(model, "coef_"):
                        # For logistic regression coefficients can indicate feature impact
                        importances = model.coef_[0]
                        
                    if importances is not None:
                        importance_path = os.path.join(IMPORTANCE_DIR, f"{exp_name}_importance.csv")
                        pd.DataFrame({
                            "descriptor": desc_features,
                            "importance": importances
                        }).sort_values(by="importance", key=abs, ascending=False).to_csv(importance_path, index=False)
                        
                # 10. Save Model Artifact (for reproducibility)
                model_path = os.path.join(MODELS_DIR, f"{exp_name}_model.joblib")
                joblib.dump({
                    "model": model,
                    "scaler": scaler_obj,
                    "feature_names": desc_features if rep_name == "descriptors" else None
                }, model_path)
                
    # 11. Create and save the Comparison Matrix
    results_df = pd.DataFrame(results_list)
    results_df.to_csv(os.path.join(RESULTS_DIR, "model_comparison.csv"), index=False)
    print("\nSaved model comparison matrix to: results/model_comparison.csv")
    
    # Generate and write MD table
    write_md_table(results_df)

def write_md_table(results_df):
    md_path = os.path.join(RESULTS_DIR, "model_comparison.md")
    
    table_rows = ""
    for _, row in results_df.iterrows():
        table_rows += f"| {row['model']} | {row['representation']} | {row['split']} | {row['train_n']} | {row['test_n']} | {row['accuracy']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['f1']:.4f} | {row['macro_f1']:.4f} | {row['roc_auc']:.4f} | {row['pr_auc']:.4f} |\n"
        
    markdown_content = f"""# Model Performance Comparison Matrix — MoleculeScope

This table contains the comparative results of all 18 primary experiments and the majority-class baselines.

| Model | Representation | Split | Train N | Test N | Accuracy | Precision | Recall | F1 | Macro F1 | ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
{table_rows}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Human-readable comparison table written to: {md_path}")

if __name__ == "__main__":
    main()
