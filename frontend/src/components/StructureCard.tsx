import React from "react";

interface StructureCardProps {
  svg: string;
  compoundName: string | null;
  formula: string;
  inchikey: string;
  canonicalSmiles: string;
}

export const StructureCard: React.FC<StructureCardProps> = ({ svg, compoundName, formula, inchikey, canonicalSmiles }) => {
  return (
    <div className="card">
      <span className="muted">Structure</span>
      <div className="mol-box" dangerouslySetInnerHTML={{ __html: svg }} />
      {compoundName && <div className="mol-name">{compoundName}</div>}
      <div className="identity-rows" style={{ marginTop: compoundName ? 0 : "14px" }}>
        <div className="identity-row">
          <span className="k">formula</span>
          <span className="v">{formula}</span>
        </div>
        {inchikey && (
          <div className="identity-row">
            <span className="k">inchikey</span>
            <span className="v">{inchikey}</span>
          </div>
        )}
        <div className="identity-row">
          <span className="k">canonical</span>
          <span className="v">{canonicalSmiles}</span>
        </div>
      </div>
    </div>
  );
};
