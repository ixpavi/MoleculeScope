import numpy as np
import pandas as pd
from rdkit import Chem
from .fingerprints import compute_single_morgan_fingerprint

def run_descriptor_checks(desc_df):
    """
    Runs sanity checks on the calculated descriptors.
    
    Args:
        desc_df (pd.DataFrame): Descriptor matrix.
        
    Returns:
        dict: Summary statistics and check flags.
    """
    stats = {}
    
    # a. Missing and Infinite values
    nan_counts = desc_df.isna().sum().to_dict()
    inf_counts = desc_df.apply(lambda col: np.isinf(col).sum()).to_dict()
    
    # b. Constant feature check
    variances = desc_df.var(ddof=0).to_dict()
    constant_features = [name for name, var in variances.items() if var == 0.0]
    
    # c. Range inspection
    for col in desc_df.columns:
        series = desc_df[col].dropna()
        stats[col] = {
            "nan_count": int(nan_counts[col]),
            "inf_count": int(inf_counts[col]),
            "min": float(series.min()) if not series.empty else 0.0,
            "max": float(series.max()) if not series.empty else 0.0,
            "mean": float(series.mean()) if not series.empty else 0.0,
            "median": float(series.median()) if not series.empty else 0.0,
            "std": float(series.std()) if not series.empty else 0.0,
            "constant": col in constant_features
        }
        
    # d. Correlation analysis
    corr_matrix = desc_df.corr().abs()
    high_corr_pairs = []
    cols = desc_df.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr_matrix.iloc[i, j]
            if val >= 0.90:  # Threshold of 0.90 for high correlation
                high_corr_pairs.append({
                    "feature_1": cols[i],
                    "feature_2": cols[j],
                    "correlation": float(val)
                })
                
    return {
        "descriptor_stats": stats,
        "constant_features": constant_features,
        "high_correlation_pairs": high_corr_pairs
    }

def run_fingerprint_checks(fp_matrix):
    """
    Runs sanity checks on Morgan fingerprints.
    
    Args:
        fp_matrix (np.ndarray): 2D array of shape (num_molecules, nBits).
        
    Returns:
        dict: Stats on active bits, types, and NaN presence.
    """
    num_mols, nbits = fp_matrix.shape
    
    # NaN/Inf check
    nan_count = int(np.isnan(fp_matrix).sum())
    inf_count = int(np.isinf(fp_matrix).sum())
    
    # Active bits (sum along row axis)
    active_bits_per_mol = fp_matrix.sum(axis=1)
    
    active_stats = {
        "nan_count": nan_count,
        "inf_count": inf_count,
        "data_type": str(fp_matrix.dtype),
        "total_bits_per_molecule": nbits,
        "min_active_bits": int(active_bits_per_mol.min()) if len(active_bits_per_mol) > 0 else 0,
        "max_active_bits": int(active_bits_per_mol.max()) if len(active_bits_per_mol) > 0 else 0,
        "mean_active_bits": float(active_bits_per_mol.mean()) if len(active_bits_per_mol) > 0 else 0.0,
        "median_active_bits": float(np.median(active_bits_per_mol)) if len(active_bits_per_mol) > 0 else 0.0,
        "average_density_pct": float(active_bits_per_mol.mean() / nbits * 100) if nbits > 0 else 0.0
    }
    
    return active_stats

def verify_fingerprint_determinism(smiles="CN1C=NC2=C1C(=O)N(C(=O)N2C)C"):
    """
    Verifies that fingerprints generated twice from the same SMILES are identical.
    
    Args:
        smiles (str): Target SMILES string (default is Caffeine).
        
    Returns:
        bool: True if deterministic, False otherwise.
    """
    mol1 = Chem.MolFromSmiles(smiles)
    mol2 = Chem.MolFromSmiles(smiles)
    
    fp1 = compute_single_morgan_fingerprint(mol1)
    fp2 = compute_single_morgan_fingerprint(mol2)
    
    if fp1 is None or fp2 is None:
        return False
        
    return np.array_equal(fp1, fp2)
