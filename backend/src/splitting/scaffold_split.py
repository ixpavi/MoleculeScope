import numpy as np
import pandas as pd
from collections import defaultdict
from .split_utils import compute_scaffold

def generate_scaffold_split(df, smiles_col="SMILES", train_ratio=0.80):
    """
    Groups molecules by Bemis-Murcko scaffold and splits them deterministically
    into Train and Test sets using a greedy bin-packing algorithm.
    
    Acyclic molecules (empty scaffold) are treated as unique singleton groups 
    to prevent cluster skew.
    
    Args:
        df (pd.DataFrame): Dataframe to split. Assumes index is reset (0 to len-1).
        smiles_col (str): Column name containing SMILES.
        train_ratio (float): Target ratio of training set size.
        
    Returns:
        tuple: (train_indices, test_indices, scaffold_stats)
    """
    # Group indices by scaffold
    scaffold_groups = defaultdict(list)
    
    for idx, row in df.iterrows():
        s = row[smiles_col]
        scaffold = compute_scaffold(s)
        
        if scaffold == "":
            # Acyclic compounds are treated as singletons
            scaffold_groups[f"acyclic_{idx}"].append(idx)
        else:
            scaffold_groups[scaffold].append(idx)
            
    # Sort groups by size in descending order, using scaffold string as a tie-breaker
    # to guarantee complete determinism.
    sorted_groups = sorted(
        scaffold_groups.items(), 
        key=lambda x: (len(x[1]), x[0]), 
        reverse=True
    )
    
    total_samples = len(df)
    target_train_size = int(total_samples * train_ratio)
    
    train_idx = []
    test_idx = []
    
    # Greedy bin packing
    for scaffold, group_indices in sorted_groups:
        if len(train_idx) + len(group_indices) <= target_train_size:
            train_idx.extend(group_indices)
        else:
            test_idx.extend(group_indices)
            
    # Verification checks
    train_set = set(train_idx)
    test_set = set(test_idx)
    assert len(train_set.intersection(test_set)) == 0, "CRITICAL ERROR: Scaffold overlap detected!"
    assert len(train_set) + len(test_set) == total_samples, "CRITICAL ERROR: Missing elements in split!"
    
    # Calculate stats
    num_unique_scaffolds = len([s for s in scaffold_groups.keys() if not s.startswith("acyclic_")])
    num_acyclic = len([s for s in scaffold_groups.keys() if s.startswith("acyclic_")])
    
    stats = {
        "num_unique_scaffolds": num_unique_scaffolds,
        "num_acyclic_singletons": num_acyclic,
        "total_groups": len(scaffold_groups)
    }
    
    return train_idx, test_idx, stats
