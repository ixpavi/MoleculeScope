import numpy as np
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.DataStructs import ConvertToNumpyArray

DEFAULT_RADIUS = 2
DEFAULT_NBITS = 2048
DEFAULT_USE_CHIRALITY = False

def compute_single_morgan_fingerprint(mol, radius=DEFAULT_RADIUS, nBits=DEFAULT_NBITS, use_chirality=DEFAULT_USE_CHIRALITY):
    """
    Computes a binary Morgan fingerprint for a single RDKit Mol object.
    
    Args:
        mol (Chem.Mol): RDKit molecule object.
        radius (int): Circular radius parameter (default=2, equivalent to diameter=4 or ECFP4).
        nBits (int): Dimensionality of hashed bit vector (default=2048).
        use_chirality (bool): Whether stereochemical environments are incorporated (default=False).
        
    Returns:
        np.ndarray: Binary 1D NumPy array of shape (nBits,) containing 0s and 1s, or None if parsing fails.
    """
    if mol is None:
        return None
        
    try:
        fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(
            mol,
            radius=radius,
            nBits=nBits,
            useChirality=use_chirality
        )
        arr = np.zeros((nBits,), dtype=np.int8)
        ConvertToNumpyArray(fp, arr)
        return arr
    except Exception:
        return None

def compute_fingerprints_matrix(df, smiles_col="SMILES", radius=DEFAULT_RADIUS, nBits=DEFAULT_NBITS, use_chirality=DEFAULT_USE_CHIRALITY):
    """
    Computes binary Morgan fingerprints for a DataFrame containing a SMILES column.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        smiles_col (str): Column name containing SMILES.
        radius (int): Morgan radius.
        nBits (int): Morgan bit count.
        use_chirality (bool): Chirality setting.
        
    Returns:
        np.ndarray: Binary 2D NumPy array of shape (len(df), nBits) with type np.int8.
    """
    num_rows = len(df)
    fp_matrix = np.zeros((num_rows, nBits), dtype=np.int8)
    
    for idx, (original_idx, row) in enumerate(df.iterrows()):
        s = row[smiles_col]
        mol = Chem.MolFromSmiles(s)
        arr = compute_single_morgan_fingerprint(mol, radius=radius, nBits=nBits, use_chirality=use_chirality)
        if arr is not None:
            fp_matrix[idx, :] = arr
        else:
            # In case of failure, keep it as zeros
            pass
            
    return fp_matrix
