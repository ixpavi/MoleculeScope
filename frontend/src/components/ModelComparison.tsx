import React from "react";

export const ModelComparison: React.FC = () => {
  const models = [
    {
      name: "Random Forest + Descriptors",
      selected: true,
      accuracy: 0.7447,
      macroF1: 0.7212,
      rocAuc: 0.8017,
      prAuc: 0.8504,
      desc: "Selected for production. Best scaffold generalization (F1/Accuracy) with minimal inputs (11 features), zero scaling dependancy, and strong physical explainability.",
    },
    {
      name: "XGBoost + Combined",
      selected: false,
      accuracy: 0.7280,
      macroF1: 0.6838,
      rocAuc: 0.8138,
      prAuc: 0.8684,
      desc: "Marginally higher ROC-AUC / PR-AUC, but poorer F1 generalization (-3.74%) and suffers from significant high-dimensionality overhead (2,059 features).",
    },
    {
      name: "Logistic Regression + Combined",
      selected: false,
      accuracy: 0.7146,
      macroF1: 0.6668,
      rocAuc: 0.7865,
      prAuc: 0.8445,
      desc: "High generalization decay. Suffers from linear constraints on non-linear molecular representations.",
    },
  ];

  return (
    <div className="card" style={{ marginTop: "1.5rem" }}>
      <h2 className="card-title">Model Family Benchmarks</h2>
      <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>
        Scaffold-split generalization metrics evaluated during the model-selection phase (Phase 5).
      </p>

      <div className="table-container">
        <table className="scientific-table">
          <thead>
            <tr>
              <th>Model Configuration</th>
              <th>Accuracy</th>
              <th>Macro F1</th>
              <th>ROC-AUC</th>
              <th>PR-AUC</th>
            </tr>
          </thead>
          <tbody>
            {models.map((m) => (
              <React.Fragment key={m.name}>
                <tr className={m.selected ? "highlight-row" : ""}>
                  <td style={{ fontWeight: 600 }}>
                    {m.name} {m.selected && <span style={{ fontSize: "0.75rem", color: "var(--color-primary)", marginLeft: "0.25rem" }}>(Production Select)</span>}
                  </td>
                  <td>{(m.accuracy * 100).toFixed(2)}%</td>
                  <td>{m.macroF1.toFixed(4)}</td>
                  <td>{m.rocAuc.toFixed(4)}</td>
                  <td>{m.prAuc.toFixed(4)}</td>
                </tr>
                <tr className={m.selected ? "highlight-row" : ""}>
                  <td colSpan={5} style={{ fontSize: "0.75rem", color: "var(--text-muted)", paddingBottom: "1rem", borderBottomWidth: "2px" }}>
                    {m.desc}
                  </td>
                </tr>
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
