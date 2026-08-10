import sys
import os
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.rdMolDescriptors import CalcMolFormula

# Add backend to path to import features descriptors
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.features.descriptors import compute_single_descriptors, get_descriptor_names

# The largest SMILES in the cleaned B3DB training set is 338 characters; this cap is a
# generous multiple of that, chosen to reject pathological inputs (used as a cheap parsing
# DoS guard on /predict, /predict/batch, and /explain) without ever rejecting a real molecule.
MAX_SMILES_LENGTH = 1000

def validate_and_parse_smiles(smiles: str):
    """
    Validates a SMILES string.
    Returns (is_valid, mol_or_error_message).
    """
    if not smiles or not smiles.strip():
        return False, "SMILES input cannot be empty or whitespace-only."

    if len(smiles) > MAX_SMILES_LENGTH:
        return False, f"SMILES input exceeds the maximum allowed length of {MAX_SMILES_LENGTH} characters."

    try:
        mol = Chem.MolFromSmiles(smiles)
    except Exception as e:
        return False, f"Error parsing SMILES: {str(e)}"
        
    if mol is None or mol.GetNumAtoms() == 0:
        return False, f"Invalid or malformed SMILES string: '{smiles}'."
        
    return True, mol

def generate_molecule_svg(mol, width: int = 300, height: int = 300) -> str:
    """Generates a compact molecular structure SVG string using RDKit's 2D drawer."""
    if mol is None or mol.GetNumAtoms() == 0:
        return ""
    try:
        # Create a copy so compute coordinates doesn't modify the original mol permanently
        mol_copy = Chem.Mol(mol)
        rdDepictor.Compute2DCoords(mol_copy)
        
        # Prepare SVG canvas
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        
        # Clean rendering options
        options = drawer.drawOptions()
        options.clearBackground = True
        options.addStereoAnnotation = True
        
        drawer.DrawMolecule(mol_copy)
        drawer.FinishDrawing()
        
        svg = drawer.GetDrawingText()
        return svg
    except Exception:
        return ""

def process_molecule(smiles: str):
    """
    Parses a SMILES, canonicalizes it, calculates formula, SVG, and 11 descriptors.
    Returns a dict with molecule details.
    """
    is_valid, mol_or_err = validate_and_parse_smiles(smiles)
    if not is_valid:
        raise ValueError(mol_or_err)
        
    mol = mol_or_err
    canonical_smiles = Chem.MolToSmiles(mol, canonical=True)
    molecular_formula = CalcMolFormula(mol)
    svg_str = generate_molecule_svg(mol)
    try:
        inchikey = Chem.MolToInchiKey(mol)
    except Exception:
        inchikey = ""

    # Calculate descriptors using the verified Phase 2/6 module
    desc_dict = compute_single_descriptors(mol)

    # Ensure all descriptors exist and are aligned to the exact list
    descriptors = {}
    for name in get_descriptor_names():
        val = desc_dict.get(name)
        # Convert values to standard floats for serialization consistency
        descriptors[name] = float(val) if val is not None else 0.0

    return {
        "canonical_smiles": canonical_smiles,
        "molecular_formula": molecular_formula,
        "inchikey": inchikey,
        "svg": svg_str,
        "descriptors": descriptors,
        "mol_object": mol
    }
