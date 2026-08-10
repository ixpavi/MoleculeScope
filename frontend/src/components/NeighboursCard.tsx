import React from "react";

interface NearestNeighbor {
  name: string;
  smiles: string;
  bbb_label: string;
  similarity: number;
}

interface NeighboursCardProps {
  maxSimilarity: number | null;
  neighbors: NearestNeighbor[];
  currentPrediction: "BBB+" | "BBB-";
}

export const NeighboursCard: React.FC<NeighboursCardProps> = ({ maxSimilarity, neighbors, currentPrediction }) => {
  return (
    <div className="card">
      <div className="card-h">
        <span className="muted">Applicability domain</span>
        <span className="meta-mono">
          {maxSimilarity !== null ? `max T ${maxSimilarity.toFixed(2)}` : "unavailable"}
          {maxSimilarity !== null && (maxSimilarity >= 0.4 ? " · inside domain" : " · sparse region")}
        </span>
      </div>
      {neighbors.length === 0 ? (
        <span className="meta-mono" style={{ display: "block", marginTop: "14px" }}>
          Similarity search unavailable.
        </span>
      ) : (
        <>
          <div className="nn-table" style={{ marginTop: "14px" }}>
            <div className="desc-head" style={{ padding: "0 0 8px" }}>NEAREST TRAINING MOLECULE</div>
            <div className="desc-head" style={{ padding: "0 0 8px", textAlign: "right" }}>TANIMOTO</div>
            <div className="desc-head" style={{ padding: "0 0 8px", textAlign: "right" }}>TRUE</div>
            <div className="desc-head" style={{ padding: "0 0 8px", textAlign: "right" }}>AGREE</div>
          </div>
          <div className="nn-table">
            {neighbors.map((n, idx) => {
              const agrees = n.bbb_label === currentPrediction;
              return (
                <div className="nn-row" key={`${n.name}-${idx}`}>
                  <div style={{ color: "var(--text)", textTransform: "capitalize", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {n.name}
                  </div>
                  <div style={{ textAlign: "right" }}>{n.similarity.toFixed(2)}</div>
                  <div style={{ textAlign: "right", color: n.bbb_label === "BBB+" ? "var(--accent)" : "var(--neg)" }}>
                    {n.bbb_label === "BBB+" ? "BBB+" : "BBB−"}
                  </div>
                  <div style={{ textAlign: "right", color: "var(--dim)" }}>{agrees ? "✓" : "✗"}</div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};
