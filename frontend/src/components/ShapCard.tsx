import React, { useEffect, useState } from "react";

interface ShapContribution {
  descriptor: string;
  descriptor_value: number;
  shap_value: number;
}

interface ExplanationResponse {
  base_value: number;
  contributions: ShapContribution[];
}

const SHORT_LABELS: Record<string, string> = {
  "Molecular Weight": "MolWt",
  "LogP": "MolLogP",
  "TPSA": "TPSA",
  "H-Bond Donors": "NumHDonors",
  "H-Bond Acceptors": "NumHAcceptors",
  "Rotatable Bonds": "NumRotatableBonds",
  "Ring Count": "RingCount",
  "Aromatic Ring Count": "NumAromaticRings",
  "Heavy Atom Count": "HeavyAtomCount",
  "Fraction CSP3": "FractionCSP3",
  "Formal Charge": "FormalCharge",
};

interface ShapCardProps {
  smiles: string;
}

export const ShapCard: React.FC<ShapCardProps> = ({ smiles }) => {
  const [data, setData] = useState<ExplanationResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setError(false);

    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
    fetch(`${apiBaseUrl}/api/explain`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ smiles }),
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((json) => {
        if (!Array.isArray(json?.contributions)) throw new Error("malformed");
        if (!cancelled) setData(json);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });

    return () => {
      cancelled = true;
    };
  }, [smiles]);

  if (error) return null;

  const maxAbs = data ? Math.max(...data.contributions.map((c) => Math.abs(c.shap_value))) : 1;

  return (
    <div className="card">
      <div className="card-h">
        <span className="muted">SHAP attribution</span>
        <span className="meta-mono">base {data ? data.base_value.toFixed(3) : "—"}</span>
      </div>
      <div style={{ marginTop: "14px" }}>
        {!data && <span className="meta-mono">Computing...</span>}
        {data &&
          data.contributions.map((c) => {
            const isPositive = c.shap_value >= 0;
            const widthPct = (Math.abs(c.shap_value) / maxAbs) * 100;
            return (
              <div className="shap-row" key={c.descriptor}>
                <span style={{ color: "var(--text)" }}>{SHORT_LABELS[c.descriptor] || c.descriptor}</span>
                <span className="shap-neg">{!isPositive && <i style={{ width: `${widthPct}%` }} />}</span>
                <span className="shap-pos">{isPositive && <i style={{ width: `${widthPct}%` }} />}</span>
                <span style={{ textAlign: "right", color: "var(--dim)" }}>
                  {isPositive ? "+" : ""}
                  {c.shap_value.toFixed(3)}
                </span>
              </div>
            );
          })}
      </div>
    </div>
  );
};
