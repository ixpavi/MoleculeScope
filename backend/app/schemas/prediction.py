from pydantic import BaseModel, Field, ConfigDict

class SMILESRequest(BaseModel):
    """SMILES string input request model."""
    smiles: str = Field(
        ...,
        description="SMILES string representing the molecular structure to predict.",
        examples=["CN1C(=O)N(C)c2ncn(C)c2C1=O"]
    )

class DescriptorSchema(BaseModel):
    """Calculated RDKit physicochemical descriptors schema."""
    Molecular_Weight: float = Field(..., alias="Molecular Weight")
    LogP: float
    TPSA: float
    H_Bond_Donors: float = Field(..., alias="H-Bond Donors")
    H_Bond_Acceptors: float = Field(..., alias="H-Bond Acceptors")
    Rotatable_Bonds: float = Field(..., alias="Rotatable Bonds")
    Ring_Count: float = Field(..., alias="Ring Count")
    Aromatic_Ring_Count: float = Field(..., alias="Aromatic Ring Count")
    Heavy_Atom_Count: float = Field(..., alias="Heavy Atom Count")
    Fraction_CSP3: float = Field(..., alias="Fraction CSP3")
    Formal_Charge: float = Field(..., alias="Formal Charge")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "Molecular Weight": 194.194,
                "LogP": -1.0293,
                "TPSA": 61.82,
                "H-Bond Donors": 0.0,
                "H-Bond Acceptors": 3.0,
                "Rotatable Bonds": 0.0,
                "Ring Count": 2.0,
                "Aromatic Ring Count": 2.0,
                "Heavy Atom Count": 14.0,
                "Fraction CSP3": 0.375,
                "Formal Charge": 0.0
            }
        }
    )

class NearestNeighbor(BaseModel):
    """Single training-set molecule found via applicability domain similarity search."""
    name: str = Field(..., description="Compound name from the training dataset (not independently verified).")
    smiles: str = Field(..., description="Canonical SMILES of the training-set neighbor.")
    bbb_label: str = Field(..., description="Ground-truth BBB+/BBB- label of this training-set molecule.")
    similarity: float = Field(..., description="Tanimoto similarity (0-1) between the query and this neighbor's Morgan fingerprint.")


class ApplicabilityDomain(BaseModel):
    """Estimates whether the query molecule resembles anything the model was trained on."""
    max_similarity: float | None = Field(None, description="Tanimoto similarity to the single closest training-set molecule; null if unavailable.")
    nearest_neighbors: list[NearestNeighbor] = Field(default_factory=list, description="Top training-set molecules by Tanimoto similarity, most similar first.")


class VoteHistogramBin(BaseModel):
    """Single bucket of the 250-tree vote histogram."""
    bin_start: float = Field(..., description="Lower edge of this probability bucket (inclusive), 0-1.")
    bin_end: float = Field(..., description="Upper edge of this probability bucket (exclusive), 0-1.")
    count: int = Field(..., description="Number of trees whose predicted BBB+ probability falls in this bucket.")
    height_pct: float = Field(..., description="Bucket count as a percentage of the tallest bucket, for direct use as a bar height (0-100).")


class ModelUncertainty(BaseModel):
    """Spread of individual decision-tree votes within the Random Forest, as a proxy for prediction stability. Not a calibrated confidence interval."""
    tree_probability_std: float = Field(..., description="Standard deviation of per-tree BBB+ probability votes across all 250 trees.")
    tree_probability_iqr_low: float = Field(..., description="25th percentile of per-tree BBB+ probability votes.")
    tree_probability_iqr_high: float = Field(..., description="75th percentile of per-tree BBB+ probability votes.")
    tree_count: int = Field(..., description="Total number of trees in the Random Forest ensemble (250).")
    trees_voting_bbb_plus: int = Field(..., description="Number of individual trees whose vote (probability >= 0.5) favors BBB+.")
    vote_histogram: list[VoteHistogramBin] = Field(default_factory=list, description="Real 20-bucket histogram of the 250 individual tree votes across [0, 1].")


class DescriptorPercentile(BaseModel):
    """Where a single descriptor value sits within the real training distribution."""
    percentile: float = Field(..., description="Percentile rank (0-100) of this value within the 7,795-molecule training set for this descriptor.")
    position: float = Field(..., description="Normalized 0-1 position between the training set's observed min and max, for placing a distribution marker.")


class PredictionResponse(BaseModel):
    """Predict endpoint response structure."""
    prediction: str = Field(..., description="BBB permeability prediction class: BBB+ or BBB-.")
    probability_bbb_plus: float = Field(..., description="Predicted probability of BBB+ (permeable).")
    probability_bbb_minus: float = Field(..., description="Predicted probability of BBB- (impermeable).")
    canonical_smiles: str = Field(..., description="Standardized canonical SMILES notation.")
    molecular_formula: str = Field(..., description="Molecular formula calculated from elements.")
    inchikey: str = Field("", description="RDKit-computed InChIKey, a fixed-length hashed structure identifier.")
    svg: str = Field(..., description="2D structure rendering SVG string.")
    descriptors: DescriptorSchema = Field(..., description="Calculated 11 physicochemical descriptors.")
    applicability_domain: ApplicabilityDomain = Field(..., description="Nearest-neighbor similarity to the training set, as a rough out-of-distribution flag.")
    uncertainty: ModelUncertainty = Field(..., description="Spread of individual tree votes in the Random Forest ensemble.")
    descriptor_percentiles: dict[str, DescriptorPercentile] = Field(default_factory=dict, description="Per-descriptor percentile rank within the real training distribution, keyed by descriptor name.")

class HealthResponse(BaseModel):
    """Health check response structure."""
    status: str = Field("ok", description="Server status indicator.")
    model_loaded: bool = Field(..., description="Boolean indicating if the production model is loaded.")
    model_type: str = Field(..., description="Type of the serialized ML classifier.")
    model_version: str = Field(..., description="Version of the production model.")


class BatchRowResponse(BaseModel):
    """Row level result for batch prediction."""
    row_index: int = Field(..., description="1-indexed row number from the input CSV.")
    input_smiles: str = Field(..., description="Original raw SMILES string uploaded.")
    status: str = Field(..., description="Status of the prediction: success or error.")
    error: str | None = Field(None, description="Error message if status is error, else null.")
    prediction: str | None = Field(None, description="BBB permeability class: BBB+ or BBB- (null if error).")
    probability_bbb_plus: float | None = Field(None, description="Predicted probability of BBB+ (null if error).")
    probability_bbb_minus: float | None = Field(None, description="Predicted probability of BBB- (null if error).")
    canonical_smiles: str | None = Field(None, description="RDKit canonicalized SMILES representation (null if error).")
    molecular_formula: str | None = Field(None, description="Molecular formula calculated from atoms (null if error).")
    descriptors: DescriptorSchema | None = Field(None, description="Calculated 11 descriptors (null if error).")
    extra_columns: dict[str, str] = Field(default_factory=dict, description="Preserved extra metadata columns for row tracking.")


class BatchSummary(BaseModel):
    """Overview statistics for bulk screening run."""
    filename: str = Field(..., description="Name of the processed CSV file.")
    total_rows: int = Field(..., description="Total non-empty data rows parsed.")
    processed_rows: int = Field(..., description="Total rows predicted successfully.")
    failed_rows: int = Field(..., description="Total rows with errors.")
    bbb_plus_count: int = Field(..., description="Total BBB+ permeable predicted count.")
    bbb_minus_count: int = Field(..., description="Total BBB- impermeable predicted count.")


class BatchPredictionResponse(BaseModel):
    """Batch screening response payload structure."""
    summary: BatchSummary = Field(..., description="Overview summary metrics.")
    results: list[BatchRowResponse] = Field(..., description="List of row-level prediction outputs.")


class MoleculeSearchResult(BaseModel):
    """Single compound-name search match, sourced from the cleaned B3DB dataset."""
    name: str = Field(..., description="Compound name as recorded in the source B3DB dataset (not independently verified), or a hand-verified common name if verified=true.")
    smiles: str = Field(..., description="Canonical SMILES for this entry. Render the structure to visually confirm identity before trusting the name.")
    verified: bool = Field(False, description="True for a small hand-curated list of common drug names known to be missing or mislabeled in the raw dataset; false for raw dataset matches.")
    group_consistent: bool | None = Field(None, description="For raw (non-verified) entries that share a name with other results: whether this entry's Morgan fingerprint is similar enough (Tanimoto >= 0.5) to at least one other same-named entry to be a plausible variant (e.g. stereoisomer) rather than a likely data-entry error. Null if this name has no other entries to compare against, or if verified=true.")


class MoleculeSearchResponse(BaseModel):
    """Compound name search response structure."""
    results: list[MoleculeSearchResult] = Field(..., description="Matching compounds, best match first, limited to the requested count.")


class GlobalImportanceItem(BaseModel):
    """Single descriptor's global importance ranking entry."""
    descriptor: str = Field(..., description="Descriptor name.")
    importance: float = Field(..., description="Gini-based feature importance from the frozen production model, in [0, 1].")


class GlobalImportanceResponse(BaseModel):
    """Global feature importance response structure."""
    feature_importances: list[GlobalImportanceItem] = Field(..., description="11 descriptors ranked by importance, descending.")


class ShapContribution(BaseModel):
    """Single descriptor's SHAP contribution for one molecule's prediction."""
    descriptor: str = Field(..., description="Descriptor name.")
    descriptor_value: float = Field(..., description="Calculated value of this descriptor for the input molecule.")
    shap_value: float = Field(..., description="Signed contribution to the BBB+ class log-odds/probability output (positive pushes toward BBB+).")


class ExplanationResponse(BaseModel):
    """Local SHAP explanation response structure for a single SMILES prediction."""
    canonical_smiles: str = Field(..., description="Standardized canonical SMILES notation.")
    prediction: str = Field(..., description="BBB permeability prediction class: BBB+ or BBB-.")
    probability_bbb_plus: float = Field(..., description="Predicted probability of BBB+ (permeable).")
    base_value: float = Field(..., description="SHAP expected value (average model output over the background dataset) for the BBB+ class.")
    contributions: list[ShapContribution] = Field(..., description="Per-descriptor SHAP contributions, sorted by absolute magnitude descending.")

