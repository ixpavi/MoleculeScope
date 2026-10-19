import React, { useMemo, useState } from "react";
import { FlaskConical, RefreshCw } from "lucide-react";

const MAX_CANDIDATES = 4;

interface CandidateInput {
  id: number;
  smiles: string;
}

interface PredictionResult {
  prediction: "BBB+" | "BBB-";
  probability_bbb_plus: number;
  canonical_smiles: string;
  descriptors: Record<string, number>;
  applicability_domain?: { max_similarity?: number | null };
  uncertainty?: { tree_probability_std?: number };
}

interface CandidateResult {
  id: number;
  result?: PredictionResult;
  error?: string;
}

const INITIAL_CANDIDATES: CandidateInput[] = Array.from({ length: MAX_CANDIDATES }, (_, index) => ({
  id: index + 1,
  smiles: "",
}));

export const ComparePage: React.FC = () => {
  const [candidates, setCandidates] = useState<CandidateInput[]>(INITIAL_CANDIDATES);
  const [results, setResults] = useState<CandidateResult[]>([]);
  const [loading, setLoading] = useState(false);

  const filledCandidates = useMemo(
    () => candidates.filter((candidate) => candidate.smiles.trim()),
    [candidates],
  );

  const setCandidate = (id: number, smiles: string) => {
    setCandidates((current) => current.map((candidate) => (
      candidate.id === id ? { ...candidate, smiles } : candidate
    )));
    setResults([]);
  };

  const loadExamples = () => {
    // Two CNS-active drugs against two antibiotics that stay out of the brain,
    // so the example shows a BBB+ / BBB- contrast rather than four similar results.
    setCandidates([
      { id: 1, smiles: "CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21" },                            // diazepam
      { id: 2, smiles: "CN1C(=O)N(C)c2ncn(C)c2C1=O" },                                     // caffeine
      { id: 3, smiles: "CC1(C)SC2C(NC(=O)Cc3ccccc3)C(=O)N2C1C(=O)O" },                     // penicillin G
      { id: 4, smiles: "COC1(NC(=O)C(C(=O)O)c2ccc(O)cc2)C(=O)N2C(C(=O)O)=C(CSc3nnnn3C)COC21" }, // moxalactam
    ]);
    setResults([]);
  };

  const handleCompare = async () => {
    if (!filledCandidates.length) return;

    setLoading(true);
    setResults([]);
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";

    const nextResults = await Promise.all(filledCandidates.map(async (candidate): Promise<CandidateResult> => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/predict`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ smiles: candidate.smiles.trim() }),
        });
        const data = await response.json();
        if (!response.ok) {
          return { id: candidate.id, error: data?.detail || "Prediction could not be completed." };
        }
        return { id: candidate.id, result: data as PredictionResult };
      } catch {
        return { id: candidate.id, error: "Unable to reach the prediction service." };
      }
    }));

    setResults(nextResults);
    setLoading(false);
  };

  return (
    <div className="page-shell compare-page">
      <div className="compare-intro">
        <div>
          <h1 className="page-title">Candidate comparison</h1>
          <p className="page-description">
            Score up to four molecules with the production model and inspect the evidence that separates them.
          </p>
        </div>
        <button type="button" className="example-btn" onClick={loadExamples} disabled={loading}>
          Load example set
        </button>
      </div>

      <section className="card" aria-labelledby="candidate-inputs-title">
        <h2 className="card-title" id="candidate-inputs-title"><FlaskConical size={17} /> Candidate set</h2>
        <div className="compare-inputs">
          {candidates.map((candidate) => (
            <label className="compare-input" key={candidate.id}>
              <span className="compare-input-label"><span>Candidate {candidate.id}</span><span>SMILES</span></span>
              <textarea
                value={candidate.smiles}
                onChange={(event) => setCandidate(candidate.id, event.target.value)}
                placeholder="Paste a SMILES string"
                disabled={loading}
                aria-label={`Candidate ${candidate.id} SMILES`}
              />
            </label>
          ))}
        </div>
        <div className="compare-actions">
          <p className="compare-note">
            Each candidate is evaluated independently by the same frozen Random Forest. Predicted probability of BBB+ is not a calibrated confidence score.
          </p>
          <button type="button" className="predict-btn" onClick={handleCompare} disabled={loading || !filledCandidates.length}>
            {loading ? <><RefreshCw className="spinner" size={15} /> Comparing...</> : `Compare ${filledCandidates.length || ""} candidate${filledCandidates.length === 1 ? "" : "s"}`}
          </button>
        </div>
      </section>

      {results.length > 0 && (
        <section aria-live="polite" aria-label="Candidate comparison results">
          <div className="card-h" style={{ marginBottom: "var(--space-sm)" }}>
            <h2 className="card-title" style={{ margin: 0 }}>Model comparison</h2>
            <span className="meta-mono">shared production model · independent inferences</span>
          </div>
          <div className="compare-results">
            {results.map((entry) => {
              const candidate = candidates.find((item) => item.id === entry.id);
              if (!entry.result) {
                return <article className="compare-result" key={entry.id}><span className="compare-candidate-name">Candidate {entry.id}</span><p className="compare-error">{entry.error}</p></article>;
              }
              const { result } = entry;
              const isPlus = result.prediction === "BBB+";
              const similarity = result.applicability_domain?.max_similarity;
              const voteSpread = result.uncertainty?.tree_probability_std;
              return (
                <article className="compare-result" key={entry.id}>
                  <div className="compare-result-top">
                    <span className="compare-candidate-name">Candidate {entry.id}</span>
                    <span className="meta-mono">{result.descriptors["Molecular Weight"]?.toFixed(1)} Da</span>
                  </div>
                  <div className={`compare-verdict ${isPlus ? "plus" : "minus"}`}>{result.prediction}</div>
                  <div className="compare-probability">BBB+ probability {result.probability_bbb_plus.toFixed(3)}</div>
                  <div className="compare-meter" aria-label={`Candidate ${entry.id} BBB plus probability`}><span style={{ width: `${result.probability_bbb_plus * 100}%` }} /></div>
                  <div className="compare-metrics">
                    <div className="compare-metric"><div className="compare-metric-label">LogP</div><div className="compare-metric-value">{result.descriptors.LogP?.toFixed(2) ?? "—"}</div></div>
                    <div className="compare-metric"><div className="compare-metric-label">TPSA</div><div className="compare-metric-value">{result.descriptors.TPSA?.toFixed(1) ?? "—"}</div></div>
                    <div className="compare-metric"><div className="compare-metric-label">Nearest Tanimoto</div><div className="compare-metric-value">{similarity == null ? "Unavailable" : similarity.toFixed(2)}</div></div>
                    <div className="compare-metric"><div className="compare-metric-label">Tree vote spread</div><div className="compare-metric-value">{voteSpread == null ? "Unavailable" : voteSpread.toFixed(3)}</div></div>
                  </div>
                  <div className="compare-smiles" title={result.canonical_smiles || candidate?.smiles}>{result.canonical_smiles || candidate?.smiles}</div>
                </article>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
};
