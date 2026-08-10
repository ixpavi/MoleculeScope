import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors

# Exact list of RDKit descriptors to compute
DESCRIPTOR_MAPPING = {
    "Molecular Weight": Descriptors.MolWt,
    "LogP": Descriptors.MolLogP,
    "TPSA": Descriptors.TPSA,
    "H-Bond Donors": Descriptors.NumHDonors,
    "H-Bond Acceptors": Descriptors.NumHAcceptors,
    "Rotatable Bonds": Descriptors.NumRotatableBonds,
    "Ring Count": Descriptors.RingCount,
    "Aromatic Ring Count": Descriptors.NumAromaticRings,
    "Heavy Atom Count": Descriptors.HeavyAtomCount,
    "Fraction CSP3": Descriptors.FractionCSP3,
    "Formal Charge": Chem.GetFormalCharge
}

def get_descriptor_names():
    """Returns list of descriptor name keys."""
    return list(DESCRIPTOR_MAPPING.keys())

def compute_single_descriptors(mol):
    """
    Computes descriptors for a single RDKit Mol object.
    
    Args:
        mol (Chem.Mol): RDKit molecule object.
        
    Returns:
        dict: Keys are descriptor names, values are calculated floats/ints.
    """
    if mol is None or mol.GetNumAtoms() == 0:
        return {name: None for name in DESCRIPTOR_MAPPING}
        
    feats = {}
    for name, func in DESCRIPTOR_MAPPING.items():
        try:
            val = func(mol)
            # Basic type cleaning (infinite values handled in checks)
            feats[name] = float(val) if val is not None else None
        except Exception:
            feats[name] = None
            
    return feats

def compute_descriptors_dataframe(df, smiles_col="SMILES"):
    """
    Computes descriptors for a pandas DataFrame containing a SMILES column.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        smiles_col (str): Column name containing SMILES.
        
    Returns:
        pd.DataFrame: Descriptor matrix with original indices.
    """
    records = []
    indices = []
    
    for idx, row in df.iterrows():
        s = row[smiles_col]
        mol = Chem.MolFromSmiles(s)
        features = compute_single_descriptors(mol)
        records.append(features)
        indices.append(idx)
        
    return pd.DataFrame(records, index=indices)
