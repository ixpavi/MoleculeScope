from rdkit import Chem
from rdkit.Chem.Scaffolds import MurckoScaffold

def compute_scaffold(smiles, include_chirality=False):
    """
    Computes the Bemis-Murcko scaffold SMILES for a given molecule.
    If the molecule has no rings (acyclic), returns an empty string "".
    
    Args:
        smiles (str): SMILES string.
        include_chirality (bool): Whether stereochemical markers are included.
        
    Returns:
        str: Scaffold SMILES string.
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return ""
        # Get standard Murcko scaffold SMILES
        scaffold_smiles = MurckoScaffold.MurckoScaffoldSmiles(
            smiles=smiles, 
            includeChirality=include_chirality
        )
        return scaffold_smiles
    except Exception:
        return ""
