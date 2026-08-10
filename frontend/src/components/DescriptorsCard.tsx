import React from "react";

interface DescriptorPercentile {
  percentile: number;
  position: number;
}

interface DescriptorsCardProps {
  descriptors: Record<string, number>;
  percentiles: Record<string, DescriptorPercentile>;
}

const DESCRIPTOR_ORDER: { key: string; label: string; decimals: number }[] = [
  { key: "Molecular Weight", label: "MolWt", decimals: 2 },
  { key: "LogP", label: "LogP", decimals: 2 },
  { key: "TPSA", label: "TPSA", decimals: 2 },
  { key: "H-Bond Donors", label: "NumHDonors", decimals: 0 },
  { key: "H-Bond Acceptors", label: "NumHAcceptors", decimals: 0 },
  { key: "Rotatable Bonds", label: "NumRotatableBonds", decimals: 0 },
  { key: "Ring Count", label: "RingCount", decimals: 0 },
  { key: "Aromatic Ring Count", label: "NumAromaticRings", decimals: 0 },
  { key: "Heavy Atom Count", label: "HeavyAtomCount", decimals: 0 },
  { key: "Fraction CSP3", label: "FractionCSP3", decimals: 3 },
  { key: "Formal Charge", label: "FormalCharge", decimals: 0 },
];

const ordinalSuffix = (n: number): string => {
  const rounded = Math.round(n);
  if (rounded % 10 === 1 && rounded % 100 !== 11) return "st";
  if (rounded % 10 === 2 && rounded % 100 !== 12) return "nd";
  if (rounded % 10 === 3 && rounded % 100 !== 13) return "rd";
  return "th";
};

export const DescriptorsCard: React.FC<DescriptorsCardProps> = ({ descriptors, percentiles }) => {
  return (
    <div className="card">
      <div className="card-h">
        <span className="muted">Descriptors</span>
        <span className="meta-mono">RDKit · 11 features</span>
      </div>
      <div className="desc-table">
        <div className="desc-head">DESCRIPTOR</div>
        <div className="desc-head" style={{ textAlign: "right" }}>VALUE</div>
        <div className="desc-head">TRAINING DISTRIBUTION</div>
        <div className="desc-head" style={{ textAlign: "right" }}>PERCENTILE</div>
        {DESCRIPTOR_ORDER.map(({ key, label, decimals }) => {
          const value = descriptors[key];
          const stats = percentiles[key];
          return (
            <div className="desc-row" key={key}>
              <div style={{ color: "var(--text)" }}>{label}</div>
              <div style={{ textAlign: "right" }}>{value !== undefined ? value.toFixed(decimals) : "—"}</div>
              <div>
                <div className="bar-track">
                  {stats && <div className="bar-mark" style={{ left: `${(stats.position * 100).toFixed(1)}%` }} />}
                </div>
              </div>
              <div style={{ textAlign: "right", color: "var(--dim)" }}>
                {stats ? `${Math.round(stats.percentile)}${ordinalSuffix(stats.percentile)}` : "—"}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
