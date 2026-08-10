import React, { useEffect, useState } from "react";

interface VoteHistogramBin {
  bin_start: number;
  bin_end: number;
  count: number;
  height_pct: number;
}

interface Uncertainty {
  tree_probability_std: number;
  tree_count: number;
  trees_voting_bbb_plus: number;
  vote_histogram: VoteHistogramBin[];
}

interface NearestNeighbor {
  name: string;
  bbb_label: string;
  similarity: number;
}

interface PredictionCardProps {
  prediction: "BBB+" | "BBB-";
  probabilityBbbPlus: number;
  uncertainty: Uncertainty;
  neighbors: NearestNeighbor[];
  canonicalSmiles: string;
}

type Tab = "votes" | "shap" | "neighbours";

const consensusLabel = (std: number): { label: string; color: string } => {
  if (std < 0.15) return { label: "high consensus", color: "var(--ok)" };
  if (std < 0.3) return { label: "moderate consensus", color: "var(--dim)" };
  return { label: "low consensus", color: "var(--neg)" };
};

export const PredictionCard: React.FC<PredictionCardProps> = ({
  prediction,
  probabilityBbbPlus,
  uncertainty,
  neighbors,
  canonicalSmiles,
}) => {
  const [tab, setTab] = useState<Tab>("votes");
  const [shapPreview, setShapPreview] = useState<{ descriptor: string; shap_value: number }[] | null>(null);

  useEffect(() => {
    if (tab !== "shap" || shapPreview) return;
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
    fetch(`${apiBaseUrl}/api/explain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ smiles: canonicalSmiles }),
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((json) => {
        if (Array.isArray(json?.contributions)) {
          setShapPreview(json.contributions.slice(0, 5));
        }
      })
      .catch(() => setShapPreview([]));
  }, [tab, canonicalSmiles, shapPreview]);

  const isBBBPlus = prediction === "BBB+";
  const consensus = consensusLabel(uncertainty.tree_probability_std);
  const maxShap = shapPreview ? Math.max(...shapPreview.map((c) => Math.abs(c.shap_value)), 0.001) : 1;

  return (
    <div className="card">
      <div className="card-h">
        <div>
          <div className="muted">Prediction</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: "16px", marginTop: "6px", flexWrap: "wrap" }}>
            <span className={`verdict ${isBBBPlus ? "" : "bbb-minus"}`}>{prediction}</span>
            <span className="meta-mono" style={{ color: consensus.color }}>
              p {probabilityBbbPlus.toFixed(3)} · {consensus.label}
            </span>
          </div>
        </div>
        <div className="segmented">
          <button type="button" className={tab === "votes" ? "on" : ""} onClick={() => setTab("votes")}>Votes</button>
          <button type="button" className={tab === "shap" ? "on" : ""} onClick={() => setTab("shap")}>SHAP</button>
          <button type="button" className={tab === "neighbours" ? "on" : ""} onClick={() => setTab("neighbours")}>Neighbours</button>
        </div>
      </div>

      {tab === "votes" && (
        <>
          <div className="hist">
            {uncertainty.vote_histogram.map((bin, idx) => (
              <i
                key={idx}
                className={bin.bin_start >= 0.5 ? "on" : "off"}
                style={{ height: `${Math.max(bin.height_pct, 2)}%` }}
              />
            ))}
          </div>
          <div style={{ height: "1px", background: "var(--line)", marginTop: "10px" }} />
          <div className="scale">
            <span>p 0.0</span>
            <span>0.25</span>
            <span>0.50 threshold</span>
            <span>0.75</span>
            <span>1.0</span>
          </div>
          <div className="meta-mono" style={{ marginTop: "12px", fontSize: "13.5px", color: "var(--dim)" }}>
            {uncertainty.trees_voting_bbb_plus} of {uncertainty.tree_count} trees vote BBB+ · σ {uncertainty.tree_probability_std.toFixed(3)}
          </div>
        </>
      )}

      {tab === "shap" && (
        <div style={{ marginTop: "26px" }}>
          {!shapPreview && <span className="meta-mono">Computing...</span>}
          {shapPreview &&
            shapPreview.map((c) => {
              const isPositive = c.shap_value >= 0;
              const widthPct = (Math.abs(c.shap_value) / maxShap) * 100;
              return (
                <div className="shap-row" key={c.descriptor}>
                  <span style={{ color: "var(--text)" }}>{c.descriptor}</span>
                  <span className="shap-neg">{!isPositive && <i style={{ width: `${widthPct}%` }} />}</span>
                  <span className="shap-pos">{isPositive && <i style={{ width: `${widthPct}%` }} />}</span>
                  <span style={{ textAlign: "right", color: "var(--dim)" }}>
                    {isPositive ? "+" : ""}
                    {c.shap_value.toFixed(3)}
                  </span>
                </div>
              );
            })}
          <div className="meta-mono" style={{ marginTop: "10px", fontSize: "13px" }}>Top 5 shown · full breakdown below</div>
        </div>
      )}

      {tab === "neighbours" && (
        <div style={{ marginTop: "26px" }}>
          {neighbors.length === 0 && <span className="meta-mono">Similarity search unavailable.</span>}
          {neighbors.slice(0, 3).map((n, idx) => (
            <div key={idx} className="shap-row" style={{ gridTemplateColumns: "1fr 80px 62px" }}>
              <span style={{ color: "var(--text)", textTransform: "capitalize" }}>{n.name}</span>
              <span style={{ textAlign: "right", color: n.bbb_label === "BBB+" ? "var(--accent)" : "var(--neg)" }}>
                {n.bbb_label === "BBB+" ? "BBB+" : "BBB−"}
              </span>
              <span style={{ textAlign: "right", color: "var(--dim)" }}>{n.similarity.toFixed(2)}</span>
            </div>
          ))}
          <div className="meta-mono" style={{ marginTop: "10px", fontSize: "13px" }}>Top 3 shown · full list below</div>
        </div>
      )}
    </div>
  );
};
