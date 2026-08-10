import os
import sys
import numpy as np
from .. import config

# Reuse the authoritative Phase 2 fingerprint implementation (radius=2, nBits=2048,
# useChirality=False) so query fingerprints are computed identically to the training set.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.features.fingerprints import compute_single_morgan_fingerprint


class ApplicabilityDomainService:
    """Lazily loads the precomputed training-set Morgan fingerprint matrix (row-aligned
    with the cleaned B3DB dataset) and answers nearest-neighbor Tanimoto similarity
    queries. This estimates whether a query molecule resembles anything the production
    model was actually trained on ("applicability domain" in QSAR terminology) — the
    frozen model itself has no such notion and will score arbitrarily novel structures
    with the same apparent confidence as familiar ones.

    Degrades to an empty neighbor list if the fingerprint matrix or dataset is
    unavailable, rather than failing predictions that don't need it.
    """

    def __init__(self):
        self._fingerprints = None
        self._row_sums = None
        self._names = None
        self._smiles = None
        self._labels = None
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        self._loaded = True

        if not os.path.exists(config.FINGERPRINTS_PATH) or not os.path.exists(config.CLEANED_DATASET_PATH):
            return

        import csv

        with np.load(config.FINGERPRINTS_PATH) as data:
            key = "fingerprints" if "fingerprints" in data else list(data.keys())[0]
            fingerprints = data[key].astype(np.float32)

        names, smiles_list, labels = [], [], []
        with open(config.CLEANED_DATASET_PATH, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                names.append((row.get("compound_name") or "").strip() or "(unnamed)")
                smiles_list.append((row.get("canonical_smiles") or "").strip())
                labels.append((row.get("BBB+/BBB-") or "").strip())

        if len(names) != fingerprints.shape[0]:
            # Row alignment can't be guaranteed if these ever drift apart; refuse rather
            # than silently return mismatched neighbor identities.
            return

        self._fingerprints = fingerprints
        self._row_sums = fingerprints.sum(axis=1)
        self._names = names
        self._smiles = smiles_list
        self._labels = labels

    def nearest_neighbors(self, mol, k: int = 5) -> dict:
        self._load()

        if self._fingerprints is None:
            return {"max_similarity": None, "nearest_neighbors": []}

        query_fp = compute_single_morgan_fingerprint(mol)
        if query_fp is None:
            return {"max_similarity": None, "nearest_neighbors": []}

        query_fp = query_fp.astype(np.float32)
        query_sum = float(query_fp.sum())
        if query_sum == 0:
            return {"max_similarity": None, "nearest_neighbors": []}

        intersection = self._fingerprints @ query_fp
        union = self._row_sums + query_sum - intersection
        # Avoid division by zero for any all-zero training fingerprint rows.
        tanimoto = np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)

        top_k_idx = np.argsort(-tanimoto)[:k]

        neighbors = [
            {
                "name": self._names[i],
                "smiles": self._smiles[i],
                "bbb_label": self._labels[i],
                "similarity": float(tanimoto[i]),
            }
            for i in top_k_idx
        ]

        return {
            "max_similarity": float(tanimoto[top_k_idx[0]]) if len(top_k_idx) > 0 else None,
            "nearest_neighbors": neighbors,
        }


applicability_domain_service = ApplicabilityDomainService()
