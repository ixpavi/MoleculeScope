import React, { useEffect, useState } from "react";
import { Download, FlaskConical, Layers, ScanSearch, GitBranch } from "lucide-react";
import { QueryCard, type RecentEntry } from "./QueryCard";
import { PredictionCard } from "./PredictionCard";
import { DescriptorsCard } from "./DescriptorsCard";
import { StructureCard } from "./StructureCard";
import { ShapCard } from "./ShapCard";
import { NeighboursCard } from "./NeighboursCard";

const RECENT_STORAGE_KEY = "moleculescope_recent_searches";

export const PredictorPage: React.FC = () => {
  const [smiles, setSmiles] = useState("");
  const [matchedName, setMatchedName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [recent, setRecent] = useState<RecentEntry[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_STORAGE_KEY);
      if (stored) setRecent(JSON.parse(stored));
    } catch {
      // localStorage unavailable — recent list just stays empty
    }
  }, []);

  const rememberRecent = (name: string, smilesVal: string) => {
    setRecent((prev) => {
      const filtered = prev.filter((e) => e.name.toLowerCase() !== name.toLowerCase());
      const next = [{ name, smiles: smilesVal }, ...filtered].slice(0, 2);
      try {
        localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(next));
      } catch {
        // ignore write failures (private browsing, storage full, etc.)
      }
      return next;
    });
  };

  const handlePredict = async (smilesOverride?: string) => {
    const trimmedSmiles = (smilesOverride ?? smiles).trim();
    if (!trimmedSmiles) {
      setError("Please enter a SMILES string.");
      setResult(null);
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
    const endpoint = `${apiBaseUrl}/api/predict`;

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ smiles: trimmedSmiles }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data?.detail || "An unexpected error occurred during prediction.");
        setResult(null);
      } else {
        setResult(data);
        setError(null);
        if (matchedName) rememberRecent(matchedName, trimmedSmiles);
      }
    } catch {
      setError("Unable to connect to the MoleculeScope backend. Please ensure the FastAPI server is running.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSelect = (selectedSmiles: string, name: string) => {
    setSmiles(selectedSmiles);
    setMatchedName(name);
  };

  const handleSelectRecent = (entry: RecentEntry) => {
    setSmiles(entry.smiles);
    setMatchedName(entry.name);
  };

  const handleExport = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `moleculescope_prediction_${result.canonical_smiles ? "result" : "output"}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className="topbar">
        <div>
          <div className="eyebrow">SCREENING / PREDICTOR</div>
          <div className="title">MoleculeScope</div>
        </div>
        <button
          type="button"
          className="search"
          style={{ width: "auto", color: result ? "#b6a99c" : "var(--dim2)", cursor: result ? "pointer" : "not-allowed" }}
          onClick={handleExport}
          disabled={!result}
        >
          <Download size={13} /> Export
        </button>
      </div>

      {error && (
        <div className="row" style={{ gridTemplateColumns: "1fr", paddingBottom: 0 }}>
          <div className="alert alert-error" role="alert">
            <div>{error}</div>
          </div>
        </div>
      )}

      <div className="row row-2">
        {result && !loading ? (
          <PredictionCard
            prediction={result.prediction}
            probabilityBbbPlus={result.probability_bbb_plus}
            uncertainty={result.uncertainty}
            neighbors={result.applicability_domain?.nearest_neighbors || []}
            canonicalSmiles={result.canonical_smiles}
          />
        ) : (
          <div className="card" style={{ display: "flex", flexDirection: "column", justifyContent: "center", minHeight: "280px" }}>
            {loading ? (
              <div className="loading-container" style={{ padding: 0, textAlign: "center" }}>
                <span className="meta-mono">Calculating descriptors and scoring model...</span>
              </div>
            ) : (
              <div style={{ textAlign: "center" }}>
                <FlaskConical size={26} style={{ color: "var(--accent)" }} />
                <div style={{ fontFamily: "var(--f-display)", fontSize: "22px", marginTop: "14px" }}>
                  Screen a molecule
                </div>
                <div className="muted" style={{ marginTop: "6px", maxWidth: "360px", marginLeft: "auto", marginRight: "auto" }}>
                  Enter a SMILES string or search a compound name to predict blood-brain barrier permeability.
                </div>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    gap: "22px",
                    marginTop: "26px",
                    paddingTop: "20px",
                    borderTop: "1px solid var(--line)",
                    flexWrap: "wrap",
                  }}
                >
                  <div className="meta-mono" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <Layers size={13} style={{ color: "var(--dim)" }} /> 11 RDKit descriptors
                  </div>
                  <div className="meta-mono" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <ScanSearch size={13} style={{ color: "var(--dim)" }} /> 250-tree Random Forest
                  </div>
                  <div className="meta-mono" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <GitBranch size={13} style={{ color: "var(--dim)" }} /> Scaffold-split generalization
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        <QueryCard
          smiles={smiles}
          setSmiles={(v) => {
            setSmiles(v);
            setMatchedName(null);
          }}
          matchedName={matchedName}
          onPredict={() => handlePredict()}
          loading={loading}
          recent={recent}
          onSelectRecent={handleSelectRecent}
          onSearchSelect={handleSearchSelect}
        />
      </div>

      {result && !loading && (
        <>
          <div className="row row-2">
            <DescriptorsCard descriptors={result.descriptors} percentiles={result.descriptor_percentiles || {}} />
            <StructureCard
              svg={result.svg}
              compoundName={matchedName}
              formula={result.molecular_formula}
              inchikey={result.inchikey}
              canonicalSmiles={result.canonical_smiles}
            />
          </div>

          <div className="row row-eq" style={{ paddingBottom: "26px" }}>
            <ShapCard smiles={result.canonical_smiles} />
            <NeighboursCard
              maxSimilarity={result.applicability_domain?.max_similarity ?? null}
              neighbors={result.applicability_domain?.nearest_neighbors || []}
              currentPrediction={result.prediction}
            />
          </div>
        </>
      )}
    </>
  );
};
