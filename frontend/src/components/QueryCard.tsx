import React from "react";
import { Loader2 } from "lucide-react";
import { MoleculeSearchInput } from "./MoleculeSearchInput";

export interface RecentEntry {
  name: string;
  smiles: string;
}

interface QueryCardProps {
  smiles: string;
  setSmiles: (val: string) => void;
  matchedName: string | null;
  onPredict: () => void;
  loading: boolean;
  recent: RecentEntry[];
  onSelectRecent: (entry: RecentEntry) => void;
  onSearchSelect: (smiles: string, name: string) => void;
}

export const QueryCard: React.FC<QueryCardProps> = ({
  smiles,
  setSmiles,
  matchedName,
  onPredict,
  loading,
  recent,
  onSelectRecent,
  onSearchSelect,
}) => {
  const isDisabled = !smiles.trim() || loading;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (smiles.trim()) onPredict();
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <span className="muted">Query</span>

      <div className="field">
        <div className="k">SMILES</div>
        <textarea
          id="smiles-input"
          rows={2}
          value={smiles}
          onChange={(e) => setSmiles(e.target.value)}
          placeholder="CN1C(=O)N(C)c2ncn(C)c2C1=O"
          disabled={loading}
        />
      </div>

      <div className="or">
        <span className="line" />
        <span>or</span>
        <span className="line" />
      </div>

      <div className="field">
        <div className="k">COMPOUND NAME</div>
        <MoleculeSearchInput
          bare
          onSelect={onSearchSelect}
          disabled={loading}
          placeholder="e.g. ibuprofen, caffeine, morphine..."
        />
      </div>
      {matchedName && (
        <div className="meta-mono" style={{ marginTop: "8px", color: "var(--ok)" }}>
          matched · {matchedName}
        </div>
      )}

      <button type="submit" className="btn" disabled={isDisabled}>
        {loading ? (
          <>
            <Loader2 className="spinner" size={15} />
            Running...
          </>
        ) : (
          "Run prediction  ›"
        )}
      </button>

      {recent.length > 0 && (
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "14px" }} className="meta-mono">
          <span>recent</span>
          <span>
            {recent.map((entry, idx) => (
              <React.Fragment key={entry.name}>
                <button
                  type="button"
                  onClick={() => onSelectRecent(entry)}
                  style={{ background: "none", border: "none", color: "var(--dim)", cursor: "pointer", font: "inherit", padding: 0, textTransform: "capitalize" }}
                >
                  {entry.name}
                </button>
                {idx < recent.length - 1 && " · "}
              </React.Fragment>
            ))}
          </span>
        </div>
      )}
    </form>
  );
};
