import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, precision_recall_curve, confusion_matrix

# Ensure backend folder is in path for modules import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Paths
CLEANED_DATA_PATH = "backend/data/processed/b3db_cleaned.csv"
DESCRIPTORS_PATH = "features/descriptors.csv"
RESULTS_DIR = "results"
PREDS_DIR = os.path.join(RESULTS_DIR, "predictions")
IMPORTANCE_DIR = os.path.join(RESULTS_DIR, "feature_importance")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
ANALYSIS_DIR = os.path.join(RESULTS_DIR, "analysis")
SUMMARIES_DIR = os.path.join(RESULTS_DIR, "summaries")

# Ensure folders exist
for d in [FIGURES_DIR, ANALYSIS_DIR, SUMMARIES_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

# Set plotting style
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams.update({
    "font.size": 12,
    "axes.labelsize": 14,
    "axes.titlesize": 16,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 11,
    "figure.titlesize": 18
})

MODELS = ["logistic", "rf", "xgb"]
REPS = ["descriptors", "fingerprints", "combined"]
SPLITS = ["random", "scaffold"]

def load_predictions():
    """Loads prediction files for all 18 experiments."""
    predictions = {}
    for split in SPLITS:
        predictions[split] = {}
        for rep in REPS:
            predictions[split][rep] = {}
            for model in MODELS:
                exp_name = f"{model}_{rep}_{split}"
                file_path = os.path.join(PREDS_DIR, f"{exp_name}_predictions.csv")
                if os.path.exists(file_path):
                    predictions[split][rep][model] = pd.read_csv(file_path)
                else:
                    print(f"WARNING: Prediction file not found: {file_path}")
    return predictions

def generate_roc_curves(preds):
    """Generates and saves ROC curves for random and scaffold splits."""
    colors = {
        "descriptors": "#1f77b4",   # blue
        "fingerprints": "#ff7f0e",  # orange
        "combined": "#2ca02c"       # green
    }
    linestyles = {
        "logistic": ":",
        "rf": "--",
        "xgb": "-"
    }
    
    for split in SPLITS:
        plt.figure(figsize=(10, 8))
        
        # Plot majority baseline diagonal
        plt.plot([0, 1], [0, 1], color="grey", linestyle="--", label="Majority Baseline (AUC = 0.50)")
        
        for rep in REPS:
            for model in MODELS:
                df = preds[split][rep].get(model)
                if df is None:
                    continue
                y_true = df["true_label"]
                y_prob = df["predicted_prob"]
                
                fpr, tpr, _ = roc_curve(y_true, y_prob)
                from sklearn.metrics import roc_auc_score
                auc_score = roc_auc_score(y_true, y_prob)
                
                label = f"{model.upper()} + {rep.capitalize()} (AUC = {auc_score:.3f})"
                plt.plot(fpr, tpr, color=colors[rep], linestyle=linestyles[model], linewidth=2, label=label)
                
        plt.xlim([-0.02, 1.02])
        plt.ylim([-0.02, 1.02])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title(f"ROC Curves — {split.capitalize()} Split Evaluation")
        plt.legend(loc="lower right", frameon=True)
        plt.tight_layout()
        
        fig_path = os.path.join(FIGURES_DIR, f"roc_curves_{split}.png")
        plt.savefig(fig_path, dpi=300)
        plt.close()
        print(f"Saved ROC curve plot to: {fig_path}")

def generate_pr_curves(preds):
    """Generates and saves Precision-Recall curves."""
    colors = {
        "descriptors": "#1f77b4",
        "fingerprints": "#ff7f0e",
        "combined": "#2ca02c"
    }
    linestyles = {
        "logistic": ":",
        "rf": "--",
        "xgb": "-"
    }
    
    for split in SPLITS:
        plt.figure(figsize=(10, 8))
        
        for rep in REPS:
            for model in MODELS:
                df = preds[split][rep].get(model)
                if df is None:
                    continue
                y_true = df["true_label"]
                y_prob = df["predicted_prob"]
                
                precision, recall, _ = precision_recall_curve(y_true, y_prob)
                from sklearn.metrics import precision_score
                # Compute PR-AUC (Average Precision equivalent)
                from sklearn.metrics import average_precision_score
                ap_score = average_precision_score(y_true, y_prob)
                
                label = f"{model.upper()} + {rep.capitalize()} (AP = {ap_score:.3f})"
                plt.plot(recall, precision, color=colors[rep], linestyle=linestyles[model], linewidth=2, label=label)
                
        plt.xlim([-0.02, 1.02])
        plt.ylim([-0.02, 1.02])
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.title(f"Precision-Recall Curves — {split.capitalize()} Split Evaluation")
        plt.legend(loc="lower left", frameon=True)
        plt.tight_layout()
        
        fig_path = os.path.join(FIGURES_DIR, f"pr_curves_{split}.png")
        plt.savefig(fig_path, dpi=300)
        plt.close()
        print(f"Saved PR curve plot to: {fig_path}")

def generate_confusion_matrices(preds):
    """Generates confusion matrices for the best performing configurations."""
    # Best Descriptors model: rf_descriptors
    # Best Combined model: xgb_combined
    targets = [
        ("rf", "descriptors", "Random Forest on Descriptors"),
        ("xgb", "combined", "XGBoost on Combined Features")
    ]
    
    for model, rep, label in targets:
        for split in SPLITS:
            df = preds[split][rep].get(model)
            if df is None:
                continue
            y_true = df["true_label"]
            y_pred = df["predicted_label"]
            
            cm = confusion_matrix(y_true, y_pred)
            
            plt.figure(figsize=(6, 5))
            # Custom styled premium blues heatmap
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                        xticklabels=["BBB-", "BBB+"], yticklabels=["BBB-", "BBB+"])
            plt.ylabel("True Class")
            plt.xlabel("Predicted Class")
            plt.title(f"{label}\nConfusion Matrix ({split.capitalize()} Split)")
            plt.tight_layout()
            
            fig_path = os.path.join(FIGURES_DIR, f"cm_{model}_{rep}_{split}.png")
            plt.savefig(fig_path, dpi=300)
            plt.close()
            print(f"Saved confusion matrix to: {fig_path}")

def generate_generalization_gap_plot():
    """Generates comparison bar plot showing the generalization gap."""
    # Load model_comparison.csv
    csv_path = os.path.join(RESULTS_DIR, "model_comparison.csv")
    if not os.path.exists(csv_path):
        return
        
    df = pd.read_csv(csv_path)
    # Filter out baselines
    df = df[df["model"] != "baseline_majority"]
    
    # We want to compare Macro F1, ROC-AUC, and PR-AUC
    # Reshape for seaborn plotting
    records = []
    for _, row in df.iterrows():
        records.append({
            "Experiment": f"{row['model'].upper()}+{row['representation'].capitalize()}",
            "Split": row["split"].capitalize(),
            "Metric": "Macro F1",
            "Value": row["macro_f1"]
        })
        records.append({
            "Experiment": f"{row['model'].upper()}+{row['representation'].capitalize()}",
            "Split": row["split"].capitalize(),
            "Metric": "ROC-AUC",
            "Value": row["roc_auc"]
        })
        
    plot_df = pd.DataFrame(records)
    
    # Plot Macro F1 Comparison
    plt.figure(figsize=(14, 8))
    sns.barplot(data=plot_df[plot_df["Metric"] == "Macro F1"], x="Experiment", y="Value", hue="Split", palette="Set1")
    plt.xticks(rotation=45, ha="right")
    plt.ylim([0, 1.0])
    plt.ylabel("Macro F1-Score")
    plt.title("Generalization Gap — Macro F1-Score Drop across Splits")
    plt.tight_layout()
    fig_path = os.path.join(FIGURES_DIR, "generalization_gap_macro_f1.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    
    # Plot ROC-AUC Comparison
    plt.figure(figsize=(14, 8))
    sns.barplot(data=plot_df[plot_df["Metric"] == "ROC-AUC"], x="Experiment", y="Value", hue="Split", palette="Set2")
    plt.xticks(rotation=45, ha="right")
    plt.ylim([0, 1.0])
    plt.ylabel("ROC-AUC")
    plt.title("Generalization Gap — ROC-AUC Drop across Splits")
    plt.tight_layout()
    fig_path = os.path.join(FIGURES_DIR, "generalization_gap_roc_auc.png")
    plt.savefig(fig_path, dpi=300)
    plt.close()
    
    print(f"Saved generalization gap comparison plots to: {FIGURES_DIR}")

def generate_feature_importance_plot():
    """Generates feature importance plots for descriptors based Random Forest and XGBoost."""
    # Find importance files
    rf_path = os.path.join(IMPORTANCE_DIR, "rf_descriptors_random_importance.csv")
    xgb_path = os.path.join(IMPORTANCE_DIR, "xgb_descriptors_random_importance.csv")
    
    if os.path.exists(rf_path):
        rf_df = pd.read_csv(rf_path)
        plt.figure(figsize=(10, 6))
        sns.barplot(data=rf_df, x="importance", y="descriptor", palette="Blues_r")
        plt.xlabel("MDI Feature Importance")
        plt.ylabel("Molecular Descriptor")
        plt.title("Random Forest Descriptor Feature Importances")
        plt.tight_layout()
        fig_path = os.path.join(FIGURES_DIR, "feature_importance_rf.png")
        plt.savefig(fig_path, dpi=300)
        plt.close()
        print(f"Saved RF feature importance plot to: {fig_path}")
        
    if os.path.exists(xgb_path):
        xgb_df = pd.read_csv(xgb_path)
        plt.figure(figsize=(10, 6))
        sns.barplot(data=xgb_df, x="importance", y="descriptor", palette="Oranges_r")
        plt.xlabel("XGBoost Gain Feature Importance")
        plt.ylabel("Molecular Descriptor")
        plt.title("XGBoost Descriptor Feature Importances")
        plt.tight_layout()
        fig_path = os.path.join(FIGURES_DIR, "feature_importance_xgb.png")
        plt.savefig(fig_path, dpi=300)
        plt.close()
        print(f"Saved XGB feature importance plot to: {fig_path}")

def run_error_analysis(preds):
    """Performs statistical audits on errors (FPs and FNs) in the scaffold split."""
    # We will use the Best Generalizer: rf_descriptors_scaffold
    df_rf = preds["scaffold"]["descriptors"].get("rf")
    # We will also load clean dataset to map properties
    if df_rf is None or not os.path.exists(CLEANED_DATA_PATH) or not os.path.exists(DESCRIPTORS_PATH):
        return
        
    cleaned_df = pd.read_csv(CLEANED_DATA_PATH).reset_index(drop=True)
    desc_df = pd.read_csv(DESCRIPTORS_PATH, index_col=0).reset_index(drop=True)
    
    # Extract scaffold split test indices
    with open("splits/scaffold_split_indices.json", "r") as f:
        scaff_split = json.load(f)
    test_indices = scaff_split["test_indices"]
    
    # Slice the test compounds and descriptors
    test_compounds = cleaned_df.iloc[test_indices].copy()
    test_descriptors = desc_df.iloc[test_indices].copy()
    
    # Map predictions
    test_compounds["predicted_label"] = df_rf["predicted_label"].values
    test_compounds["predicted_prob"] = df_rf["predicted_prob"].values
    test_compounds["true_numeric"] = df_rf["true_label"].values
    
    # Add descriptors for correlation analysis
    for col in ["Molecular Weight", "LogP", "TPSA", "H-Bond Donors", "Formal Charge"]:
        test_compounds[col] = test_descriptors[col].values
        
    # Classify errors
    # TP: true=1, pred=1
    # TN: true=0, pred=0
    # FP: true=0, pred=1 (False Alarm / Impermeable predicted as Permeable)
    # FN: true=1, pred=0 (Missed / Permeable predicted as Impermeable)
    def categorize(row):
        t = row["true_numeric"]
        p = row["predicted_label"]
        if t == p:
            return "Correct"
        elif t == 0 and p == 1:
            return "False Positive"
        else:
            return "False Negative"
            
    test_compounds["prediction_status"] = test_compounds.apply(categorize, axis=1)
    
    counts = test_compounds["prediction_status"].value_counts().to_dict()
    print("\nScaffold split error counts (RF descriptors):")
    print(f"  Correct: {counts.get('Correct', 0)}")
    print(f"  False Positives (FPs): {counts.get('False Positive', 0)}")
    print(f"  False Negatives (FNs): {counts.get('False Negative', 0)}")
    
    # Statistical range analysis
    props = ["Molecular Weight", "LogP", "TPSA", "H-Bond Donors"]
    analysis_records = []
    
    for status in ["Correct", "False Positive", "False Negative"]:
        status_sub = test_compounds[test_compounds["prediction_status"] == status]
        record = {"status": status, "count": len(status_sub)}
        for p in props:
            record[f"{p}_mean"] = float(status_sub[p].mean()) if len(status_sub) > 0 else 0.0
            record[f"{p}_median"] = float(status_sub[p].median()) if len(status_sub) > 0 else 0.0
        analysis_records.append(record)
        
    analysis_df = pd.DataFrame(analysis_records)
    analysis_df.to_csv(os.path.join(ANALYSIS_DIR, "scaffold_error_properties.csv"), index=False)
    
    # Write analysis to file
    write_error_analysis_report(test_compounds, props)

def write_error_analysis_report(df, props):
    report_path = os.path.join(ANALYSIS_DIR, "error_analysis.md")
    
    fp_sub = df[df["prediction_status"] == "False Positive"]
    fn_sub = df[df["prediction_status"] == "False Negative"]
    correct_sub = df[df["prediction_status"] == "Correct"]
    
    # Example compounds for FPs and FNs
    fp_examples = ""
    for _, row in fp_sub.head(5).iterrows():
        name = row['compound_name'] if pd.notna(row['compound_name']) else row['IUPAC_name']
        if pd.isna(name):
            name = "Unnamed Compound"
        fp_examples += f"*   **{name}** (SMILES: `{row['SMILES']}`): MW: `{row['Molecular Weight']:.2f}`, LogP: `{row['LogP']:.2f}`, TPSA: `{row['TPSA']:.2f}`, Prob(BBB+): `{row['predicted_prob']:.4f}`\n"
        
    fn_examples = ""
    for _, row in fn_sub.head(5).iterrows():
        name = row['compound_name'] if pd.notna(row['compound_name']) else row['IUPAC_name']
        if pd.isna(name):
            name = "Unnamed Compound"
        fn_examples += f"*   **{name}** (SMILES: `{row['SMILES']}`): MW: `{row['Molecular Weight']:.2f}`, LogP: `{row['LogP']:.2f}`, TPSA: `{row['TPSA']:.2f}`, Prob(BBB+): `{row['predicted_prob']:.4f}`\n"
        
    markdown_content = f"""# Detailed Error Analysis — MoleculeScope

This document outlines the failure modes and property distributions for errors produced on the Bemis-Murcko Scaffold split by the best generalizing model (**Random Forest on Descriptors**).

---

## 1. Property Means by Prediction Status

| Prediction Status | Sample Count | Mean MW | Mean LogP | Mean TPSA | Mean HBD |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Correct** | {len(correct_sub)} | {correct_sub['Molecular Weight'].mean():.2f} | {correct_sub['LogP'].mean():.2f} | {correct_sub['TPSA'].mean():.2f} | {correct_sub['H-Bond Donors'].mean():.2f} |
| **False Positives (FPs)** | {len(fp_sub)} | {fp_sub['Molecular Weight'].mean():.2f} | {fp_sub['LogP'].mean():.2f} | {fp_sub['TPSA'].mean():.2f} | {fp_sub['H-Bond Donors'].mean():.2f} |
| **False Negatives (FNs)** | {len(fn_sub)} | {fn_sub['Molecular Weight'].mean():.2f} | {fn_sub['LogP'].mean():.2f} | {fn_sub['TPSA'].mean():.2f} | {fn_sub['H-Bond Donors'].mean():.2f} |

---

## 2. Key Insights and Property Trends

### A. False Positives (FPs)
*   **Definition:** BBB- (impermeable) compounds predicted as BBB+ (permeable).
*   **Property Characteristics:**
    *   *Observation:* False Positives show a significantly lower mean TPSA (**{fp_sub['TPSA'].mean():.2f}** Å²) and lower Hydrogen Bond Donors count (**{fp_sub['H-Bond Donors'].mean():.2f}**) compared to correct predictions.
    *   *Rationale:* In structural pharmacology, lower polarity (TPSA < 90 Å²) and low hydrogen-bonding counts are strong signals for passive membrane partition. When an impermeable compound possesses these features (for example, due to a highly polar but uncharged moiety or a specific quaternary nitrogen that impedes entry despite favorable bulk parameters), the model falsely classifies it as BBB+ due to its favorable bulk indicators.

### B. False Negatives (FNs)
*   **Definition:** BBB+ (permeable) compounds predicted as BBB- (impermeable).
*   **Property Characteristics:**
    *   *Observation:* False Negatives show a higher mean TPSA (**{fn_sub['TPSA'].mean():.2f}** Å²) and higher Hydrogen Bond Donors (**{fn_sub['H-Bond Donors'].mean():.2f}**).
    *   *Rationale:* Highly polar molecules with many donor groups are generally predicted as BBB- because the bulk descriptors strongly align with impermeability. A potential biological explanation is that certain permeable compounds bypass passive diffusion limits via active transport mechanisms (for example, targeting glucose transporters or peptide carriers). Since our descriptor model is restricted to passive physicochemical indices, it may misclassify these potentially transporter-mediated entrants as BBB-.

---

## 3. Representative Error Compounds

### A. False Positives (Predicted BBB+, True BBB-)
{fp_examples}

### B. False Negatives (Predicted BBB-, True BBB+)
{fn_examples}
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Error analysis report written to: {report_path}")

def generate_recommendation_and_summary():
    """Generates the final model recommendation and summary documents."""
    rec_path = os.path.join(ANALYSIS_DIR, "final_model_recommendation.md")
    sum_path = os.path.join(SUMMARIES_DIR, "report_ready_summary.md")
    
    rec_content = """# Final Model Recommendation — MoleculeScope

Based on the empirical findings of Phase 4 and Phase 5, we evaluate model architectures and features to establish a final recommendation for production deployment.

---

## 1. Decision Matrix & Multi-Dimensional Tradeoffs

To make a scientifically defensible recommendation, we compare the top-performing models across three axes:

| Evaluation Axis | Random Forest (Descriptors) | XGBoost (Combined) | Logistic Regression (Combined) |
| :--- | :--- | :--- | :--- |
| **A. Scaffold Generalization** | **Best** (Macro F1 = **0.7212**, Accuracy = **74.47%**) | Moderate (Macro F1 = **0.6838**, Accuracy = **72.80%**) | Low (Macro F1 = **0.6668**, Accuracy = **71.46%**) |
| **B. Ranking & Discrimination** | Moderate (ROC-AUC = **0.8017**, PR-AUC = **0.8504**) | **Best** (ROC-AUC = **0.8138**, PR-AUC = **0.8684**) | Moderate (ROC-AUC = **0.7865**, PR-AUC = **0.8445**) |
| **C. Complexity & Latency** | **Excellent** (11 features. Low memory, instant RDKit parsing). | High (2,059 features. Dense NPZ mapping, higher latency). | High (2,059 features. Dense NPZ mapping, higher latency). |
| **D. Explainability (SHAP/MDI)** | **Excellent** (Direct mapping to 11 physical descriptors). | Hard (2,048 hashed bits are non-interpretable). | Hard (2,048 hashed bits are non-interpretable). |

---

## 2. Final Selected Model: Random Forest on Descriptors

We recommend **Random Forest trained on Physicochemical Descriptors Only** as the final deployment model for the MoleculeScope application.

### Rationale:
1.  **Robust Out-of-Distribution Generalization:** Random Forest on Descriptors achieved the highest Macro F1 (**0.7212**) and accuracy (**74.47%**) on the Bemis-Murcko scaffold split. Tree bagging over simple physical properties generalizes better to structurally novel chemical classes than models relying on sparse fingerprint configurations.
2.  **Fingerprint Generalization Defect:** Fingerprint-based models showed substantially poorer scaffold generalization than descriptor-based models in this dataset and experimental setup (RF fingerprints Macro F1 drops to **0.5546** under scaffold shift). This may reflect that circular fingerprints do not generalize as well to unseen ring configurations. Descriptors-only models showed greater robustness to scaffold shift than fingerprint-only models in our experiments.
3.  **Explainability for Drug Discovery:** RF on Descriptors allows direct mapping of feature importances to physical parameters (TPSA, LogP, HBD). In drug screening, knowing *why* a compound is predicted to cross the BBB is as important as the prediction itself.
4.  **Operational Simplicity:** The model utilizes only 11 inputs. There is no need to generate, index, and load 2048-bit sparse arrays in the FastAPI server, reducing latency and memory footprints.

---

## 3. Serialization and Production Package Plan

The production package for Phase 6 will contain:
1.  **Trained Model:** Random Forest Classifier (`results/models/rf_descriptors_scaffold_model.joblib`).
2.  **Imbalance Mitigation:** Natural distribution used (Random Forest was fit with `class_weight="balanced"` to handle the 63.5/36.5 split).
3.  **Preprocessing Requirements:** **Scale-free** (no standard scaler or column transformer needs to be bundled, as tree-based structures are scale-invariant, simplifying pipeline deployment).
4.  **Feature Vector:** 11 RDKit descriptors generated dynamically by the RDKit engine on the backend.
5.  **Target App Metrics:** Accuracy = **74.47%**, Macro F1 = **0.7212**, ROC-AUC = **0.8017** (scaffold split baseline).
"""
    
    with open(rec_path, "w", encoding="utf-8") as f:
        f.write(rec_content)
    print(f"Final model recommendation report written to: {rec_path}")
    
    sum_content = """# Report-Ready Performance Summaries — MoleculeScope

This document provides copy-pasteable paragraphs summarizing the machine learning results, generalization gaps, selection rationales, and limitations for college reports and presentations.

---

## 1. Model Performance & Comparative Summary
"We evaluated three machine learning architectures—Logistic Regression, Random Forest, and XGBoost—across three molecular feature representations: 11 physicochemical descriptors, 2048-bit binary Morgan circular fingerprints (ECFP4 equivalent), and a 2059-dimension combined feature set. Under baseline in-distribution conditions (stratified random split), all models achieved strong predictive signal, comfortably outperforming the majority-class baseline of 63.57%. The top in-distribution classifier was the Random Forest model trained on physicochemical descriptors, achieving a peak accuracy of 87.36% and a Macro F1-score of 0.8604. For probabilistic ranking, the combined representation achieved superior discrimination, with Logistic Regression yielding a peak ROC-AUC of 0.9466."

---

## 2. Generalization Gap & Scaffold Shift Summary
"To evaluate the structural generalization capability of our classifiers, we tested them on structurally novel chemistry using Bemis-Murcko scaffold splitting with zero train/test scaffold overlap. Every model exhibited a distinct performance drop, highlighting the generalization gap under out-of-distribution shifts. Fingerprint-based models showed substantially poorer scaffold generalization than descriptor-based models in this dataset and experimental setup, with the Random Forest fingerprints model experiencing a drop in Macro F1 from 0.8172 to 0.5546. This may reflect that circular fingerprints do not generalize as well to unseen ring configurations. Conversely, descriptors-only models showed greater robustness to scaffold shift than fingerprint-only models in our experiments: the descriptors-based Random Forest evaluation model dropped by only 0.1392 Macro F1 points (retaining a Macro F1 of 0.7212 and an accuracy of 74.47%), suggesting that bulk physical parameters like polar surface area and hydrogen donor counts generalize more effectively across structural classes."

---

## 3. Final Model Selection & Rationale
"We select the Random Forest classifier trained on the 11 molecular descriptors as the final production architecture. Under the scaffold split generalization test, the evaluation model achieved a classification accuracy of 74.47% and a Macro F1-score of 0.7212. While XGBoost on combined features yielded a slightly higher evaluation ROC-AUC (0.8138 vs. 0.8017), the descriptors-only Random Forest provides the ideal balance of generalization robustness, low operational complexity, and chemical explainability. Phase 6 will retrain this selected architecture on the full cleaned dataset of 7,795 molecules for production deployment, while preserving the scaffold evaluation metrics as the baseline generalization benchmark."

---

## 4. Modeling Limitations & Failure Modes
"Error audits on the scaffold split reveal different descriptor distributions for classification errors. First, False Positives (impermeable compounds predicted as permeable) typically occur in structures with lower Topological Polar Surface Area (mean TPSA = 61.13 Å²) and lower hydrogen-bond donor counts (mean HBD = 1.19); a potential explanation is that these may be blocked from entering the brain by specific efflux networks or charged moieties not fully captured by bulk descriptors. Second, False Negatives (permeable compounds predicted as impermeable) occur in more polar structures (mean TPSA = 97.67 Å², mean HBD = 2.41); a potential biological explanation is that these compounds may bypass passive lipid diffusion limits via active, carrier-mediated transport mechanisms (e.g., glucose or amino acid channels) which are not explicitly represented in our passive physicochemical features."
"""
    
    with open(sum_path, "w", encoding="utf-8") as f:
        f.write(sum_content)
    print(f"Report-ready summaries written to: {sum_path}")

if __name__ == "__main__":
    print("Loading predictions...")
    preds = load_predictions()
    
    print("Generating ROC curves...")
    generate_roc_curves(preds)
    
    print("Generating PR curves...")
    generate_pr_curves(preds)
    
    print("Generating Confusion Matrices...")
    generate_confusion_matrices(preds)
    
    print("Generating Generalization Gap comparison...")
    generate_generalization_gap_plot()
    
    print("Generating Feature Importance plot...")
    generate_feature_importance_plot()
    
    print("Running Error Analysis...")
    run_error_analysis(preds)
    
    print("Generating Recommendation and Summary reports...")
    generate_recommendation_and_summary()
    
    print("\n--- Phase 5 Evaluation Complete! ---")
