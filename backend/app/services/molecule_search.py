import csv
import os
import numpy as np
from rdkit import Chem
from .. import config

# Hand-verified aliases for a handful of very common drug names that don't reliably
# surface via raw B3DB compound_name search — the dataset files many well-known drugs
# under CAS numbers or synonyms rather than their common name, and in at least one case
# (Caffeine) the literal string "caffeine" in the raw data is attached to an unrelated
# structure while the real caffeine sits under CAS "58-08-2". These SMILES are the same
# ones already used and tested elsewhere in this app (SmilesInput.tsx example buttons,
# backend/tests/test_api.py), not newly introduced values.
#
# These are surfaced as an additional, clearly-marked ("verified") top result — the raw
# dataset entries for the same query are still returned alongside them, so a user
# searching "caffeine" can see both the verified structure and the mislabeled raw entry,
# rather than either being silently hidden.
_RAW_VERIFIED_ALIASES = {
    "caffeine": {"name": "Caffeine", "smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"},
    "aspirin": {"name": "Aspirin", "smiles": "CC(=O)Oc1ccccc1C(=O)O"},
    "ibuprofen": {"name": "Ibuprofen", "smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O"},
    "paracetamol": {"name": "Paracetamol", "smiles": "CC(=O)Nc1ccc(O)cc1"},
    "acetaminophen": {"name": "Paracetamol (Acetaminophen)", "smiles": "CC(=O)Nc1ccc(O)cc1"},
}

# Below this Tanimoto similarity, two entries sharing the same compound_name are treated
# as "inconsistent" — i.e. probably NOT the same real molecule, likely a data-entry error
# from one of B3DB's ~50 merged source studies rather than a legitimate variant (e.g.
# stereoisomer or salt form). Chosen from direct measurement: real stereoisomer pairs of
# the same drug scored 0.86-1.0 in spot checks, while a confirmed mislabeled entry (an
# unrelated small molecule tagged "azithromycin" in the raw data) scored 0.08. 0.5 sits
# well clear of both.
GROUP_CONSISTENCY_THRESHOLD = 0.5


def _canonicalize_aliases(raw: dict) -> dict:
    """RDKit-canonicalize alias SMILES once at import time, so they exactly match the
    canonical_smiles format produced elsewhere (process_molecule(), the cleaned dataset),
    which makes exact-string dedup against raw dataset matches actually work."""
    canonical = {}
    for key, entry in raw.items():
        mol = Chem.MolFromSmiles(entry["smiles"])
        smiles = Chem.MolToSmiles(mol) if mol is not None else entry["smiles"]
        canonical[key] = {"name": entry["name"], "smiles": smiles}
    return canonical


VERIFIED_ALIASES = _canonicalize_aliases(_RAW_VERIFIED_ALIASES)


class MoleculeSearchService:
    """Lazily loads compound_name -> canonical_smiles pairs from the cleaned B3DB
    dataset for name-based search, so users can find a molecule without knowing its
    SMILES. This is a convenience lookup over the training dataset, independent of the
    frozen production model: if the source CSV is unavailable, search returns an empty
    result set rather than breaking the app.

    Data quality note: compound names in B3DB come from ~50 merged source studies and
    are not independently verified here. The same name occasionally appears against
    different SMILES elsewhere in the file (e.g. stereoisomers, or source data errors).
    Rather than silently picking one, every distinct (name, smiles) pair is kept and
    returned, so the caller can render the actual structure for visual confirmation. A
    small VERIFIED_ALIASES table patches the handful of very common drug names known to
    be mislabeled or hard to find in the raw data (see module docstring above).

    For every other duplicate-name group, group_consistent is computed automatically via
    Morgan fingerprint similarity (reusing features/fingerprints.npz, row-aligned with the
    cleaned dataset) rather than left for the user to guess: entries whose structure
    doesn't resemble any other entry sharing their name are flagged inconsistent=False, so
    the frontend can warn rather than silently listing a probable data error alongside
    legitimate variants.
    """

    def __init__(self):
        self._entries = None

    def _load(self):
        if self._entries is not None:
            return self._entries

        entries = []
        path = config.CLEANED_DATASET_PATH
        if os.path.exists(path):
            seen = set()
            with open(path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row_idx, row in enumerate(reader):
                    name = (row.get("compound_name") or "").strip()
                    smiles = (row.get("canonical_smiles") or "").strip()
                    if not name or not smiles:
                        continue
                    key = (name.lower(), smiles)
                    if key in seen:
                        continue
                    seen.add(key)
                    entries.append({
                        "name": name,
                        "smiles": smiles,
                        "verified": False,
                        "group_consistent": None,
                        "_row_idx": row_idx,
                    })

        if entries and os.path.exists(config.FINGERPRINTS_PATH):
            self._annotate_group_consistency(entries)

        self._entries = entries
        return self._entries

    def _annotate_group_consistency(self, entries: list[dict]) -> None:
        """Mutates entries in place, setting group_consistent for every entry that shares
        its (lowercased) name with at least one other entry."""
        try:
            with np.load(config.FINGERPRINTS_PATH) as data:
                key = "fingerprints" if "fingerprints" in data else list(data.keys())[0]
                fingerprints = data[key].astype(np.float32)
        except Exception:
            return

        groups: dict[str, list[int]] = {}
        for i, entry in enumerate(entries):
            row_idx = entry["_row_idx"]
            if row_idx >= fingerprints.shape[0]:
                continue  # row alignment drifted; skip rather than risk a wrong index
            groups.setdefault(entry["name"].lower(), []).append(i)

        for entry_indices in groups.values():
            if len(entry_indices) < 2:
                continue

            rows = [entries[i]["_row_idx"] for i in entry_indices]
            group_fps = fingerprints[rows]
            row_sums = group_fps.sum(axis=1)
            intersection = group_fps @ group_fps.T
            union = row_sums[:, None] + row_sums[None, :] - intersection
            tanimoto = np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)
            np.fill_diagonal(tanimoto, -1)  # exclude self-comparison from the max

            best_match = tanimoto.max(axis=1)
            for local_idx, entry_idx in enumerate(entry_indices):
                entries[entry_idx]["group_consistent"] = bool(best_match[local_idx] >= GROUP_CONSISTENCY_THRESHOLD)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        query = (query or "").strip().lower()
        if not query:
            return []

        entries = self._load()
        starts_with = []
        contains = []
        for entry in entries:
            name_lower = entry["name"].lower()
            if name_lower.startswith(query):
                starts_with.append(entry)
            elif query in name_lower:
                contains.append(entry)

        starts_with.sort(key=lambda e: (len(e["name"]), e["name"]))
        contains.sort(key=lambda e: (len(e["name"]), e["name"]))

        # Hand-verified aliases (see VERIFIED_ALIASES docstring) surface first, ahead of
        # raw dataset matches, when the query matches or prefixes a known alias key.
        verified_matches = [
            {"name": alias["name"], "smiles": alias["smiles"], "verified": True, "group_consistent": None}
            for alias_key, alias in VERIFIED_ALIASES.items()
            if alias_key.startswith(query) or query in alias_key
        ]
        verified_smiles = {v["smiles"] for v in verified_matches}
        # Avoid showing the exact same structure twice if the raw dataset also has it
        # under a different label (e.g. Aspirin's raw entry is literally named "50-78-2").
        raw_matches = [
            {"name": e["name"], "smiles": e["smiles"], "verified": e["verified"], "group_consistent": e["group_consistent"]}
            for e in (starts_with + contains)
            if e["smiles"] not in verified_smiles
        ]

        return (verified_matches + raw_matches)[:limit]


molecule_search_service = MoleculeSearchService()
