import pytest
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.services.model_loader import ModelLoader, ModelLoadError, model_loader

# Benchmark descriptor values verified in Phase 6
CAFFEINE_BENCHMARK = [
    194.19399999999996, -1.029300000000001, 61.82, 0.0, 3.0, 0.0, 2.0, 2.0, 14.0, 0.375, 0.0
]
ASPIRIN_BENCHMARK = [
    180.15899999999996, 1.3101, 63.60000000000001, 1.0, 3.0, 2.0, 1.0, 1.0, 13.0, 0.1111111111111111, 0.0
]

@pytest.fixture
def client():
    """Fixture that initializes the FastAPI TestClient within a lifespan context manager."""
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    """Test 1 - Verify server is alive and production model loaded successfully."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["model_type"] == "RandomForestClassifier"
    assert data["model_version"] == "1.0.0"

def verify_molecule_response(response):
    """Utility helper to verify core response properties."""
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["prediction"] in ["BBB+", "BBB-"]
    
    assert "probability_bbb_plus" in data
    assert "probability_bbb_minus" in data
    p_plus = data["probability_bbb_plus"]
    p_minus = data["probability_bbb_minus"]
    assert 0.0 <= p_plus <= 1.0
    assert 0.0 <= p_minus <= 1.0
    assert np.isclose(p_plus + p_minus, 1.0)
    
    assert "canonical_smiles" in data
    assert "molecular_formula" in data
    assert "svg" in data
    assert data["svg"].startswith("<svg") or data["svg"].startswith("<?xml")
    
    assert "descriptors" in data
    assert len(data["descriptors"]) == 11

def test_prediction_caffeine(client):
    """Test 2 - Verify Caffeine prediction and details."""
    response = client.post("/api/predict", json={"smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"})
    verify_molecule_response(response)
    data = response.json()
    assert data["molecular_formula"] == "C8H10N4O2"

def test_prediction_aspirin(client):
    """Test 3 - Verify Aspirin prediction and details."""
    response = client.post("/api/predict", json={"smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    verify_molecule_response(response)
    data = response.json()
    assert data["molecular_formula"] == "C9H8O4"

def test_prediction_ibuprofen(client):
    """Test 4 - Verify Ibuprofen prediction and details."""
    response = client.post("/api/predict", json={"smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O"})
    verify_molecule_response(response)
    data = response.json()
    assert data["molecular_formula"] == "C13H18O2"

def test_prediction_paracetamol(client):
    """Test 5 - Verify Paracetamol prediction and details."""
    response = client.post("/api/predict", json={"smiles": "CC(=O)Nc1ccc(O)cc1"})
    verify_molecule_response(response)
    data = response.json()
    assert data["molecular_formula"] == "C8H9NO2"

def test_prediction_empty_input(client):
    """Test 6 - Verify empty and whitespace inputs return HTTP 400."""
    for empty in ["", "   ", "\n", "\t"]:
        response = client.post("/api/predict", json={"smiles": empty})
        assert response.status_code == 400
        assert "SMILES input cannot be empty or whitespace-only" in response.json()["detail"]

def test_prediction_malformed(client):
    """Test 7 - Verify invalid chemical SMILES return HTTP 400."""
    for malformed in ["NOT_A_SMILES", "C=C=C=C=C(C)C=O!!!", "C12345"]:
        response = client.post("/api/predict", json={"smiles": malformed})
        assert response.status_code == 400
        assert "Invalid or malformed SMILES string" in response.json()["detail"]

def test_prediction_missing_field(client):
    """Test 8 - Verify missing field payload returns HTTP 422."""
    response = client.post("/api/predict", json={})
    assert response.status_code == 422

def test_prediction_determinism(client):
    """Test 9 - Verify deterministic scores for identical SMILES."""
    smiles = "CN1C(=O)N(C)c2ncn(C)c2C1=O"
    
    first_res = client.post("/api/predict", json={"smiles": smiles}).json()
    for _ in range(5):
        run_res = client.post("/api/predict", json={"smiles": smiles}).json()
        assert run_res["prediction"] == first_res["prediction"]
        assert np.isclose(run_res["probability_bbb_plus"], first_res["probability_bbb_plus"])
        assert run_res["descriptors"] == first_res["descriptors"]
        assert run_res["canonical_smiles"] == first_res["canonical_smiles"]

def test_descriptor_consistency(client):
    """Test 10 - Compare computed descriptors against verified benchmarks."""
    # Caffeine Check
    res_caffeine = client.post("/api/predict", json={"smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"}).json()
    api_caffeine_feats = [res_caffeine["descriptors"][f] for f in model_loader.metadata["feature_names"]]
    assert np.allclose(api_caffeine_feats, CAFFEINE_BENCHMARK, atol=1e-5)

    # Aspirin Check
    res_aspirin = client.post("/api/predict", json={"smiles": "CC(=O)Oc1ccccc1C(=O)O"}).json()
    api_aspirin_feats = [res_aspirin["descriptors"][f] for f in model_loader.metadata["feature_names"]]
    assert np.allclose(api_aspirin_feats, ASPIRIN_BENCHMARK, atol=1e-5)

def test_model_loading_failure():
    """Test 12 - Verify model loader exception behavior on missing or invalid files."""
    loader = ModelLoader()
    
    # 1. Missing model
    with pytest.raises(ModelLoadError) as exc_info:
        loader.load(model_path="nonexistent_model.joblib", metadata_path="backend/models/production_metadata.json")
    assert "Model file not found" in str(exc_info.value)

    # 2. Missing metadata
    with pytest.raises(ModelLoadError) as exc_info:
        loader.load(model_path="backend/models/production_model.joblib", metadata_path="nonexistent_metadata.json")
    assert "Metadata file not found" in str(exc_info.value)


# --- Phase 9 Batch Prediction Tests ---

def test_batch_valid(client):
    """Test 13 - Verify that a valid batch of SMILES works and maps results correctly."""
    csv_data = (
        "SMILES,Compound_ID\n"
        "CN1C(=O)N(C)c2ncn(C)c2C1=O,CMP001\n"
        "CC(=O)Oc1ccccc1C(=O)O,CMP002\n"
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O,CMP003\n"
        "CC(=O)Nc1ccc(O)cc1,CMP004\n"
    )
    response = client.post(
        "/api/predict/batch",
        files={"file": ("valid.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Summary assertions
    summary = data["summary"]
    assert summary["filename"] == "valid.csv"
    assert summary["total_rows"] == 4
    assert summary["processed_rows"] == 4
    assert summary["failed_rows"] == 0
    assert summary["bbb_plus_count"] == 4
    assert summary["bbb_minus_count"] == 0
    
    # Results assertions
    results = data["results"]
    assert len(results) == 4
    
    # Caffeine Check
    caffeine = results[0]
    assert caffeine["row_index"] == 1
    assert caffeine["input_smiles"] == "CN1C(=O)N(C)c2ncn(C)c2C1=O"
    assert caffeine["status"] == "success"
    assert caffeine["prediction"] == "BBB+"
    assert np.isclose(caffeine["probability_bbb_plus"] + caffeine["probability_bbb_minus"], 1.0)
    assert caffeine["molecular_formula"] == "C8H10N4O2"
    assert len(caffeine["descriptors"]) == 11
    assert caffeine["extra_columns"] == {"Compound_ID": "CMP001"}
    
    # Aspirin Check
    aspirin = results[1]
    assert aspirin["row_index"] == 2
    assert aspirin["prediction"] == "BBB+"
    assert aspirin["extra_columns"] == {"Compound_ID": "CMP002"}


def test_batch_mixed_valid_invalid(client):
    """Test 14 - Verify mixed batch with valid, invalid, empty, and multi-component rows."""
    csv_data = (
        "smiles,Compound_ID\n"
        "CN1C(=O)N(C)c2ncn(C)c2C1=O,CMP001\n"
        "NOT_A_SMILES,CMP002\n"
        "  ,CMP003\n"
        "CCO.O,CMP004\n"
        "CC(=O)Oc1ccccc1C(=O)O,CMP005\n"
    )
    response = client.post(
        "/api/predict/batch",
        files={"file": ("mixed.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    
    summary = data["summary"]
    assert summary["total_rows"] == 5
    assert summary["processed_rows"] == 2
    assert summary["failed_rows"] == 3
    
    results = data["results"]
    assert len(results) == 5
    
    # Caffeine (success)
    assert results[0]["status"] == "success"
    assert results[0]["prediction"] == "BBB+"
    
    # NOT_A_SMILES (error)
    assert results[1]["status"] == "error"
    assert "Invalid or malformed SMILES string" in results[1]["error"]
    assert results[1]["prediction"] is None
    assert results[1]["extra_columns"] == {"Compound_ID": "CMP002"}
    
    # Whitespace (error)
    assert results[2]["status"] == "error"
    assert "empty or whitespace-only" in results[2]["error"]
    
    # Mixture (error)
    assert results[3]["status"] == "error"
    assert "Multi-component structures" in results[3]["error"]
    
    # Aspirin (success)
    assert results[4]["status"] == "success"


def test_batch_missing_smiles_column(client):
    """Test 15 - Verify rejection when SMILES column is missing."""
    csv_data = "SMILES_wrong,Compound_ID\nCCO,CMP001\n"
    response = client.post(
        "/api/predict/batch",
        files={"file": ("missing.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 400
    assert "Missing required SMILES column" in response.json()["detail"]


def test_batch_case_insensitive_smiles_column(client):
    """Test 16 - Verify case-insensitive match for sMiLeS column."""
    csv_data = "sMiLeS,ID\nCCO,CMP001\n"
    response = client.post(
        "/api/predict/batch",
        files={"file": ("case.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 200
    assert response.json()["summary"]["processed_rows"] == 1


def test_batch_conflicting_smiles_columns(client):
    """Test 17 - Verify duplicate/conflicting SMILES columns are rejected."""
    csv_data = "smiles,SMILES,ID\nCCO,CCO,CMP001\n"
    response = client.post(
        "/api/predict/batch",
        files={"file": ("conflict.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 400
    assert "Conflicting duplicate SMILES columns" in response.json()["detail"]


def test_batch_empty_csv(client):
    """Test 18 - Verify empty CSV returns HTTP 400."""
    response = client.post(
        "/api/predict/batch",
        files={"file": ("empty.csv", "", "text/csv")}
    )
    assert response.status_code == 400
    assert "CSV file is empty" in response.json()["detail"]


def test_batch_blank_rows(client):
    """Test 19 - Verify blank rows are skipped and do not count toward limits."""
    csv_data = (
        "smiles,ID\n"
        "CCO,CMP001\n"
        "\n"
        "  ,  \n"
        "CCN,CMP002\n"
    )
    response = client.post(
        "/api/predict/batch",
        files={"file": ("blanks.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_rows"] == 2
    assert len(data["results"]) == 2


def test_batch_duplicate_molecules(client):
    """Test 20 - Verify duplicate SMILES are processed independently and in order."""
    csv_data = "smiles,ID\nCCO,CMP001\nCCO,CMP002\n"
    response = client.post(
        "/api/predict/batch",
        files={"file": ("dups.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 2
    assert results[0]["row_index"] == 1
    assert results[0]["extra_columns"] == {"ID": "CMP001"}
    assert results[1]["row_index"] == 2
    assert results[1]["extra_columns"] == {"ID": "CMP002"}


def test_batch_oversized_file(client):
    """Test 21 - Verify file larger than 5 MB is rejected."""
    # Generate large payload > 5 MB
    large_data = "smiles\n" + "CCO\n" * 1500000
    assert len(large_data.encode("utf-8")) > 5 * 1024 * 1024
    
    response = client.post(
        "/api/predict/batch",
        files={"file": ("large.csv", large_data, "text/csv")}
    )
    assert response.status_code == 400
    assert "size exceeds the 5 MB limit" in response.json()["detail"]


def test_batch_row_limit(client):
    """Test 22 - Verify row limit > 5,000 is rejected."""
    # 5,001 data rows
    too_many_rows = "smiles\n" + "CCO\n" * 5001
    response = client.post(
        "/api/predict/batch",
        files={"file": ("too_many.csv", too_many_rows, "text/csv")}
    )
    assert response.status_code == 400
    assert "exceeds the 5,000-record limit" in response.json()["detail"]


def test_batch_model_consistency_and_determinism(client):
    """Test 23 - Verify deterministic predictions against single prediction endpoints."""
    csv_data = "smiles,ID\nCN1C(=O)N(C)c2ncn(C)c2C1=O,CMP001\n"
    
    # 1. Get prediction from batch
    res_batch = client.post(
        "/api/predict/batch",
        files={"file": ("det.csv", csv_data, "text/csv")}
    ).json()["results"][0]
    
    # 2. Get prediction from single
    res_single = client.post(
        "/api/predict",
        json={"smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"}
    ).json()
    
    assert res_batch["prediction"] == res_single["prediction"]
    assert np.isclose(res_batch["probability_bbb_plus"], res_single["probability_bbb_plus"])
    assert res_batch["descriptors"] == res_single["descriptors"]


# --- Phase 10 Explainability Tests ---

EXPECTED_DESCRIPTOR_NAMES = {
    "Molecular Weight", "LogP", "TPSA", "H-Bond Donors", "H-Bond Acceptors",
    "Rotatable Bonds", "Ring Count", "Aromatic Ring Count", "Heavy Atom Count",
    "Fraction CSP3", "Formal Charge"
}


def test_explain_global_importance(client):
    """Test 24 - Verify global feature importance endpoint returns all 11 descriptors, sorted descending, summing to ~1."""
    response = client.get("/api/explain/global")
    assert response.status_code == 200
    data = response.json()

    items = data["feature_importances"]
    assert len(items) == 11
    assert {item["descriptor"] for item in items} == EXPECTED_DESCRIPTOR_NAMES

    importances = [item["importance"] for item in items]
    assert importances == sorted(importances, reverse=True)
    assert np.isclose(sum(importances), 1.0, atol=1e-6)

    # TPSA is documented as the top production-model driver
    assert items[0]["descriptor"] == "TPSA"


def test_explain_global_deterministic(client):
    """Test 25 - Verify repeated calls return identical importances (frozen model, no retraining)."""
    r1 = client.get("/api/explain/global").json()
    r2 = client.get("/api/explain/global").json()
    assert r1 == r2


def test_explain_local_caffeine(client):
    """Test 26 - Verify local SHAP explanation for Caffeine sums to the model's actual probability."""
    response = client.post(
        "/api/explain",
        json={"smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["prediction"] == "BBB+"
    assert np.isclose(data["probability_bbb_plus"], 0.7898609017435456)

    contributions = data["contributions"]
    assert len(contributions) == 11
    assert {c["descriptor"] for c in contributions} == EXPECTED_DESCRIPTOR_NAMES

    # SHAP additivity: base_value + sum(shap_values) == model's predicted probability
    total = data["base_value"] + sum(c["shap_value"] for c in contributions)
    assert np.isclose(total, data["probability_bbb_plus"], atol=1e-6)

    # Sorted by absolute contribution magnitude, descending
    magnitudes = [abs(c["shap_value"]) for c in contributions]
    assert magnitudes == sorted(magnitudes, reverse=True)


def test_explain_local_empty_smiles(client):
    """Test 27 - Verify empty SMILES is rejected with 400."""
    response = client.post("/api/explain", json={"smiles": "   "})
    assert response.status_code == 400
    assert "empty or whitespace-only" in response.json()["detail"]


def test_explain_local_malformed_smiles(client):
    """Test 28 - Verify malformed SMILES is rejected with 400."""
    response = client.post("/api/explain", json={"smiles": "NOT_A_SMILES"})
    assert response.status_code == 400
    assert "Invalid or malformed SMILES string" in response.json()["detail"]


def test_explain_local_deterministic(client):
    """Test 29 - Verify repeated SHAP explanations for the same molecule are identical."""
    payload = {"smiles": "CC(=O)Oc1ccccc1C(=O)O"}
    r1 = client.post("/api/explain", json=payload).json()
    r2 = client.post("/api/explain", json=payload).json()
    assert r1 == r2


def test_predict_rejects_overlong_smiles(client):
    """Test - Verify a pathologically long SMILES string is rejected with a clear 400
    rather than being passed through to RDKit."""
    overlong = "C" * 5000
    response = client.post("/api/predict", json={"smiles": overlong})
    assert response.status_code == 400
    assert "exceeds the maximum allowed length" in response.json()["detail"]


def test_batch_rejects_overlong_smiles_as_row_error(client):
    """Test - Verify an overlong SMILES in a batch CSV is captured as a row-level error,
    not a crash, and doesn't block the rest of the batch."""
    overlong = "C" * 5000
    csv_data = f"smiles,ID\n{overlong},CMP001\nCCO,CMP002\n"
    response = client.post(
        "/api/predict/batch",
        files={"file": ("overlong.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["status"] == "error"
    assert "exceeds the maximum allowed length" in results[0]["error"]
    assert results[1]["status"] == "success"


def test_batch_utf8_bom_header_handled(client):
    """Test - Verify a UTF-8 BOM-prefixed CSV (as commonly exported by Excel) is still
    recognized correctly, rather than rejected with 'Missing required SMILES column'."""
    csv_bytes = "﻿smiles,ID\nCCO,CMP001\n".encode("utf-8")
    response = client.post(
        "/api/predict/batch",
        files={"file": ("excel_export.csv", csv_bytes, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["processed_rows"] == 1
    assert data["results"][0]["status"] == "success"


def test_predict_includes_applicability_domain_exact_match(client):
    """Test - Verify Caffeine (present in B3DB under CAS number '58-08-2') returns a
    max_similarity of 1.0 and a populated nearest-neighbor list."""
    response = client.post("/api/predict", json={"smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"})
    assert response.status_code == 200
    ad = response.json()["applicability_domain"]

    assert ad["max_similarity"] == pytest.approx(1.0)
    assert len(ad["nearest_neighbors"]) == 5

    top = ad["nearest_neighbors"][0]
    assert top["similarity"] == pytest.approx(1.0)
    assert top["bbb_label"] == "BBB+"

    # Sorted descending by similarity
    sims = [n["similarity"] for n in ad["nearest_neighbors"]]
    assert sims == sorted(sims, reverse=True)


def test_predict_includes_tree_uncertainty(client):
    """Test - Verify the per-tree vote spread is present and internally consistent."""
    response = client.post("/api/predict", json={"smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    assert response.status_code == 200
    unc = response.json()["uncertainty"]

    assert unc["tree_probability_std"] >= 0
    assert 0 <= unc["tree_probability_iqr_low"] <= unc["tree_probability_iqr_high"] <= 1


def test_predict_includes_inchikey(client):
    """Test - Verify the InChIKey is computed and matches the known reference value for Caffeine."""
    response = client.post("/api/predict", json={"smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"})
    assert response.status_code == 200
    assert response.json()["inchikey"] == "RYYVLZVUVIJVGH-UHFFFAOYSA-N"


def test_predict_includes_vote_histogram(client):
    """Test - Verify the real 250-tree vote histogram sums correctly and is internally consistent."""
    response = client.post("/api/predict", json={"smiles": "CN1C(=O)N(C)c2ncn(C)c2C1=O"})
    assert response.status_code == 200
    unc = response.json()["uncertainty"]

    assert unc["tree_count"] == 250
    assert 0 <= unc["trees_voting_bbb_plus"] <= 250
    histogram = unc["vote_histogram"]
    assert len(histogram) == 20
    assert sum(b["count"] for b in histogram) == 250
    assert max(b["height_pct"] for b in histogram) == 100.0
    # Bins tile [0, 1] contiguously
    assert histogram[0]["bin_start"] == pytest.approx(0.0)
    assert histogram[-1]["bin_end"] == pytest.approx(1.0)


def test_predict_includes_descriptor_percentiles(client):
    """Test - Verify descriptor percentiles are computed from the real training set for all 11 descriptors."""
    response = client.post("/api/predict", json={"smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    assert response.status_code == 200
    percentiles = response.json()["descriptor_percentiles"]

    expected_names = {
        "Molecular Weight", "LogP", "TPSA", "H-Bond Donors", "H-Bond Acceptors",
        "Rotatable Bonds", "Ring Count", "Aromatic Ring Count", "Heavy Atom Count",
        "Fraction CSP3", "Formal Charge"
    }
    assert set(percentiles.keys()) == expected_names
    for stats in percentiles.values():
        assert 0 <= stats["percentile"] <= 100
        assert 0 <= stats["position"] <= 1


def test_predict_applicability_domain_deterministic(client):
    """Test - Verify repeated predictions return identical nearest-neighbor results."""
    payload = {"smiles": "CC(C)Cc1ccc(cc1)C(C)C(=O)O"}
    r1 = client.post("/api/predict", json=payload).json()
    r2 = client.post("/api/predict", json=payload).json()
    assert r1["applicability_domain"] == r2["applicability_domain"]
    assert r1["uncertainty"] == r2["uncertainty"]


# --- Phase 11 Coverage Gap Tests ---

def test_predict_internal_error_returns_500(client, monkeypatch):
    """Test 30 - Verify an unexpected internal error during inference is reported as HTTP 500, not leaked as a traceback."""
    import app.routes.predict as predict_route

    def boom(smiles):
        raise RuntimeError("simulated internal inference failure")

    monkeypatch.setattr(predict_route, "predict_smiles", boom)

    response = client.post("/api/predict", json={"smiles": "CCO"})
    assert response.status_code == 500
    assert "An error occurred during model inference" in response.json()["detail"]


def test_health_reports_unloaded_model():
    """Test 31 - Verify /api/health reports model_loaded=False and 'None' fields when the model isn't loaded."""
    from fastapi.testclient import TestClient
    from app.main import app as fastapi_app
    from app.services.model_loader import model_loader as loader_singleton

    # Bypass the lifespan loader entirely to simulate a pre-load state.
    with TestClient(fastapi_app, raise_server_exceptions=False) as c:
        original_model, original_metadata = loader_singleton.model, loader_singleton.metadata
        try:
            loader_singleton.model = None
            loader_singleton.metadata = None
            response = c.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["model_loaded"] is False
            assert data["model_type"] == "None"
            assert data["model_version"] == "None"
        finally:
            loader_singleton.model, loader_singleton.metadata = original_model, original_metadata


def test_batch_blank_header_rejected(client):
    """Test 32 - Verify a CSV whose header row is entirely blank/whitespace is rejected as empty."""
    csv_data = " , ,\nCCO,CMP001\n"
    response = client.post(
        "/api/predict/batch",
        files={"file": ("blank_header.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 400
    assert "CSV file is empty" in response.json()["detail"]


def test_batch_all_data_rows_blank_rejected(client):
    """Test 33 - Verify a CSV with a valid header but only blank data rows is rejected as empty."""
    csv_data = "smiles,ID\n\n  ,  \n\n"
    response = client.post(
        "/api/predict/batch",
        files={"file": ("all_blank_rows.csv", csv_data, "text/csv")}
    )
    assert response.status_code == 400
    assert "CSV file is empty" in response.json()["detail"]


def test_explain_internal_error_returns_500(client, monkeypatch):
    """Test 34 - Verify an unexpected internal error during SHAP explanation is reported as HTTP 500."""
    import app.routes.explain as explain_route

    def boom(feature_vector):
        raise RuntimeError("simulated SHAP failure")

    monkeypatch.setattr(explain_route.explainability_service, "get_local_explanation", boom)

    response = client.post("/api/explain", json={"smiles": "CCO"})
    assert response.status_code == 500
    assert "An error occurred during SHAP explanation" in response.json()["detail"]


# --- Molecule Name Search Tests ---

def test_molecule_search_flags_inconsistent_duplicate_names(client):
    """Test - Verify same-name entries with wildly different structures (a real B3DB data
    error) are auto-flagged group_consistent=False, while genuine stereoisomer variants
    of the same name are flagged group_consistent=True."""
    response = client.get("/api/molecules/search", params={"q": "morphine", "limit": 10})
    assert response.status_code == 200
    results = response.json()["results"]

    morphine_entries = [r for r in results if r["name"].lower() == "morphine"]
    assert len(morphine_entries) >= 3

    consistent = [r for r in morphine_entries if r["group_consistent"] is True]
    inconsistent = [r for r in morphine_entries if r["group_consistent"] is False]
    assert len(consistent) >= 2
    assert len(inconsistent) >= 1


def test_molecule_search_group_consistent_null_for_unique_names(client):
    """Test - Verify group_consistent is null (not False) when a name has no other
    entries to compare against, and null for verified alias entries."""
    response = client.get("/api/molecules/search", params={"q": "ibuprofen"})
    assert response.status_code == 200
    results = response.json()["results"]

    verified = next(r for r in results if r["verified"] is True)
    assert verified["group_consistent"] is None

    stereo_variants = [r for r in results if "(r)-" in r["name"].lower() or "(s)-" in r["name"].lower()]
    for r in stereo_variants:
        # Each stereo-labeled name (e.g. "(r)-(-)-ibuprofen") is unique on its own —
        # nothing else shares that exact name, so there's nothing to compare against.
        assert r["group_consistent"] is None


def test_molecule_search_finds_known_compound(client):
    """Test 35 - Verify searching a known compound name (ibuprofen) returns a real match,
    with the hand-verified alias entry ranked first and marked verified."""
    response = client.get("/api/molecules/search", params={"q": "ibuprofen"})
    assert response.status_code == 200
    data = response.json()

    results = data["results"]
    assert len(results) >= 1
    assert all("ibuprofen" in r["name"].lower() for r in results)
    assert all(r["smiles"] for r in results)

    top = results[0]
    assert top["name"] == "Ibuprofen"
    assert top["verified"] is True
    assert top["smiles"] == "CC(C)Cc1ccc(C(C)C(=O)O)cc1"


def test_molecule_search_prefix_ranks_before_substring(client):
    """Test 36 - Verify prefix matches are ranked ahead of substring-only matches."""
    response = client.get("/api/molecules/search", params={"q": "morphine", "limit": 50})
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) > 1

    names = [r["name"].lower() for r in results]
    prefix_indices = [i for i, n in enumerate(names) if n.startswith("morphine")]
    substring_only_indices = [i for i, n in enumerate(names) if "morphine" in n and not n.startswith("morphine")]
    if prefix_indices and substring_only_indices:
        assert max(prefix_indices) < min(substring_only_indices)


def test_molecule_search_respects_limit(client):
    """Test 37 - Verify the limit query parameter caps the number of returned results."""
    response = client.get("/api/molecules/search", params={"q": "a", "limit": 3})
    assert response.status_code == 200
    assert len(response.json()["results"]) <= 3


def test_molecule_search_no_match_returns_empty(client):
    """Test 38 - Verify a nonsense query returns an empty result list, not an error."""
    response = client.get("/api/molecules/search", params={"q": "zzzznotarealcompoundzzzz"})
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_molecule_search_missing_query_returns_422(client):
    """Test 39 - Verify a missing required 'q' parameter is rejected as a validation error."""
    response = client.get("/api/molecules/search")
    assert response.status_code == 422


def test_molecule_search_common_drug_alias_patches_raw_data_gap(client):
    """Test 40 - Verify aspirin, which B3DB files only under CAS number '50-78-2' (not the
    name 'aspirin'), is findable via the hand-verified alias table, and that the raw
    mislabeled 'caffeine' entry is still visible alongside the verified real caffeine
    rather than being hidden."""
    aspirin_response = client.get("/api/molecules/search", params={"q": "aspirin"})
    assert aspirin_response.status_code == 200
    aspirin_results = aspirin_response.json()["results"]
    assert len(aspirin_results) == 1  # raw "50-78-2" entry deduped away (same structure)
    assert aspirin_results[0]["name"] == "Aspirin"
    assert aspirin_results[0]["verified"] is True
    assert aspirin_results[0]["smiles"] == "CC(=O)Oc1ccccc1C(=O)O"

    caffeine_response = client.get("/api/molecules/search", params={"q": "caffeine"})
    assert caffeine_response.status_code == 200
    caffeine_results = caffeine_response.json()["results"]
    assert caffeine_results[0]["name"] == "Caffeine"
    assert caffeine_results[0]["verified"] is True
    assert caffeine_results[0]["smiles"] == "Cn1c(=O)c2c(ncn2C)n(C)c1=O"
    # The raw, differently-structured dataset entry literally named "caffeine" is still
    # surfaced (not hidden), consistent with this feature's transparency design.
    assert any(r["name"] == "caffeine" and not r["verified"] for r in caffeine_results)
    assert caffeine_results[0]["smiles"] != next(r["smiles"] for r in caffeine_results if r["name"] == "caffeine")

