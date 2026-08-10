import numpy as np
from .molecule import process_molecule
from .model_loader import model_loader
from .applicability_domain import applicability_domain_service
from .descriptor_stats import descriptor_stats_service

HISTOGRAM_BIN_COUNT = 20

def _compute_tree_uncertainty(model, X) -> dict:
    """Spread of individual tree votes across the Random Forest ensemble, as a cheap
    proxy for prediction stability. Costs nothing extra to compute (model.estimators_ is
    already in memory) and requires no retraining. Also bins the real per-tree votes into
    a histogram (20 buckets across [0, 1]) so the UI can render an actual vote
    distribution rather than a simulated one."""
    tree_probs = np.array([tree.predict_proba(X)[0][1] for tree in model.estimators_])
    q1, q3 = np.percentile(tree_probs, [25, 75])

    bin_edges = np.linspace(0, 1, HISTOGRAM_BIN_COUNT + 1)
    counts, _ = np.histogram(tree_probs, bins=bin_edges)
    max_count = int(counts.max()) if counts.max() > 0 else 1
    histogram = [
        {
            "bin_start": float(bin_edges[i]),
            "bin_end": float(bin_edges[i + 1]),
            "count": int(counts[i]),
            "height_pct": round(100.0 * int(counts[i]) / max_count, 1),
        }
        for i in range(HISTOGRAM_BIN_COUNT)
    ]

    trees_voting_plus = int((tree_probs >= 0.5).sum())

    return {
        "tree_probability_std": float(tree_probs.std()),
        "tree_probability_iqr_low": float(q1),
        "tree_probability_iqr_high": float(q3),
        "tree_count": int(len(tree_probs)),
        "trees_voting_bbb_plus": trees_voting_plus,
        "vote_histogram": histogram,
    }

def predict_smiles(smiles: str):
    """
    Validates a SMILES, generates chemical metadata (formula, SVG),
    computes descriptors in the exact fixed order, and scores the production model.
    """
    # 1. Process molecule (calculates RDKit properties & descriptors)
    mol_data = process_molecule(smiles)

    # 2. Extract features in the exact fixed order required by the model
    feature_names = model_loader.metadata["feature_names"]
    feature_vector = []
    for name in feature_names:
        feature_vector.append(mol_data["descriptors"][name])

    # 3. Model Inference
    model = model_loader.model
    if model is None:
        raise RuntimeError("Production model is not loaded.")

    X = np.array([feature_vector])

    # Class prediction: 1 -> BBB+, 0 -> BBB-
    pred_class_idx = int(model.predict(X)[0])
    prediction_label = "BBB+" if pred_class_idx == 1 else "BBB-"

    # Probabilities
    probs = model.predict_proba(X)[0]
    prob_bbb_plus = float(probs[1])
    prob_bbb_minus = float(probs[0])

    # 4. Applicability domain: does this molecule resemble anything the model trained on?
    applicability_domain = applicability_domain_service.nearest_neighbors(mol_data["mol_object"])

    # 5. Tree-vote uncertainty (informational only — never presented as a confidence score)
    uncertainty = _compute_tree_uncertainty(model, X)

    # 6. Where each descriptor sits in the real 7,795-molecule training distribution
    descriptor_percentiles = {}
    for name in feature_names:
        stats = descriptor_stats_service.percentile_for(name, mol_data["descriptors"][name])
        if stats is not None:
            descriptor_percentiles[name] = stats

    return {
        "prediction": prediction_label,
        "probability_bbb_plus": prob_bbb_plus,
        "probability_bbb_minus": prob_bbb_minus,
        "canonical_smiles": mol_data["canonical_smiles"],
        "molecular_formula": mol_data["molecular_formula"],
        "inchikey": mol_data["inchikey"],
        "svg": mol_data["svg"],
        "descriptors": mol_data["descriptors"],
        "applicability_domain": applicability_domain,
        "uncertainty": uncertainty,
        "descriptor_percentiles": descriptor_percentiles
    }


def predict_smiles_batch(batch_inputs: list[dict]):
    """
    Predicts a list of SMILES inputs in batch mode using the production model.
    Each input in batch_inputs is a dict: {"row_index": int, "smiles": str, "extra_columns": dict}.
    Returns a list of dicts mapped to the BatchRowResponse schema structure.
    """
    output_rows = []
    
    # Pre-populate outputs with defaults/errors for each row
    for row in batch_inputs:
        row_idx = row["row_index"]
        smiles = row["smiles"]
        extra_cols = row["extra_columns"]
        
        output_row = {
            "row_index": row_idx,
            "input_smiles": smiles,
            "status": "error",
            "error": None,
            "prediction": None,
            "probability_bbb_plus": None,
            "probability_bbb_minus": None,
            "canonical_smiles": None,
            "molecular_formula": None,
            "descriptors": None,
            "extra_columns": extra_cols
        }
        
        # 1. Validation for empty / whitespace SMILES
        if not smiles or not smiles.strip():
            output_row["error"] = "SMILES string is empty or whitespace-only."
            output_rows.append(output_row)
            continue
            
        # 2. Validation for multi-component SMILES containing '.'
        if "." in smiles:
            output_row["error"] = "Multi-component structures (mixtures/complexes containing '.') are excluded from prediction."
            output_rows.append(output_row)
            continue
            
        # 3. Validation and processing via authoritative service
        try:
            mol_data = process_molecule(smiles)
            output_row["status"] = "success"
            output_row["canonical_smiles"] = mol_data["canonical_smiles"]
            output_row["molecular_formula"] = mol_data["molecular_formula"]
            output_row["descriptors"] = mol_data["descriptors"]
        except ValueError as e:
            output_row["error"] = str(e)
        except Exception as e:
            output_row["error"] = f"Error processing molecule: {str(e)}"
            
        output_rows.append(output_row)
        
    # Extract features for all successful rows to score the model in a single batch
    feature_names = model_loader.metadata["feature_names"]
    valid_vectors = []
    valid_indices = []
    
    for idx, row in enumerate(output_rows):
        if row["status"] == "success":
            feats = row["descriptors"]
            vector = [feats[name] for name in feature_names]
            valid_vectors.append(vector)
            valid_indices.append(idx)
            
    if valid_vectors:
        model = model_loader.model
        if model is None:
            raise RuntimeError("Production model is not loaded.")
            
        X = np.array(valid_vectors)
        
        # Batch inference
        preds = model.predict(X)
        probs = model.predict_proba(X)
        
        for i, idx in enumerate(valid_indices):
            pred_idx = int(preds[i])
            prob_plus = float(probs[i][1])
            prob_minus = float(probs[i][0])
            
            output_rows[idx]["prediction"] = "BBB+" if pred_idx == 1 else "BBB-"
            output_rows[idx]["probability_bbb_plus"] = prob_plus
            output_rows[idx]["probability_bbb_minus"] = prob_minus
            
    return output_rows

