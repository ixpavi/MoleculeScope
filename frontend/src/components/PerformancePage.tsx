import React from "react";
import { Info, HelpCircle } from "lucide-react";
import { ModelComparison } from "./ModelComparison";
import { GlobalImportanceChart } from "./GlobalImportanceChart";
import { EvaluationFigures } from "./EvaluationFigures";

export const PerformancePage: React.FC = () => {
  return (
    <div className="page-shell" style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      <div>
        <h1 className="page-title">Generalization Performance & Evaluation</h1>
        <p className="page-description">
          Review metrics, benchmark runs, baseline comparisons, and scientific limitations.
        </p>
      </div>

      {/* Critical Evaluation vs Production Disclaimer */}
      <div className="alert alert-info">
        <Info className="alert-icon" size={24} style={{ flexShrink: 0 }} />
        <div>
          <strong style={{ display: "block", marginBottom: "0.25rem", color: "var(--accent)" }}>
            Scientific Evaluation Disclaimer
          </strong>
          The metrics below represent the performance of the <strong>evaluation model</strong> trained strictly on the Bemis-Murcko scaffold train split (6,236 samples) and tested on the held-out test split (1,559 samples). The final production model was retrained on the complete dataset (7,795 molecules) to maximize molecular coverage. Therefore, these metrics serve as a generalization benchmark, not a direct measurement of the production model itself.
        </div>
      </div>

      {/* Selected Model Scaffold Metrics Cards */}
      <section className="card">
        <h2 className="card-title">Selected Model Performance (Scaffold Split)</h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.25rem" }}>
          Random Forest Classifier + 11 Physicochemical Descriptors evaluated on out-of-distribution scaffolds.
        </p>

        <div className="metrics-summary-grid">
          <div className="metric-stat-card">
            <div className="metric-label">Accuracy</div>
            <div className="metric-num">74.47%</div>
          </div>
          <div className="metric-stat-card">
            <div className="metric-label">Macro F1</div>
            <div className="metric-num" style={{ color: "var(--color-primary)" }}>0.7212</div>
          </div>
          <div className="metric-stat-card">
            <div className="metric-label">ROC-AUC</div>
            <div className="metric-num">0.8017</div>
          </div>
          <div className="metric-stat-card">
            <div className="metric-label">PR-AUC</div>
            <div className="metric-num">0.8504</div>
          </div>
        </div>

        <div style={{ display: "flex", flexWrap: "wrap", gap: "1.5rem", fontSize: "0.85rem", color: "var(--text-muted)", borderTop: "1px solid var(--border-color)", paddingTop: "1rem", marginTop: "0.5rem" }}>
          <div><strong>Train Samples:</strong> 6,236</div>
          <div><strong>Test Samples:</strong> 1,559</div>
          <div><strong>Scaffold Overlap:</strong> 0 (strictly zero scaffold leakage)</div>
        </div>
      </section>

      {/* Generalization Gap & Baselines */}
      <div className="grid-2col">
        {/* Generalization Gap Section */}
        <section className="card">
          <h2 className="card-title">Generalization Gap / Distribution Shift</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.5rem" }}>
            Performance decay when evaluating on structurally novel scaffolds vs. random interpolation.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ padding: "0.75rem", backgroundColor: "var(--bg-inset)", borderRadius: "14px", border: "1px solid var(--border-color)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Random Stratified Split (Baseline)</span>
                <span style={{ fontSize: "0.85rem", color: "var(--color-success)", fontWeight: 700 }}>87.36% Accuracy</span>
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Interpolates on randomly drawn structures. Macro F1 = 0.8604.
              </p>
            </div>

            <div style={{ padding: "0.75rem", backgroundColor: "var(--bg-inset)", borderRadius: "14px", border: "1px solid var(--border-color)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Bemis-Murcko Scaffold Split</span>
                <span style={{ fontSize: "0.85rem", color: "var(--color-warning)", fontWeight: 700 }}>74.47% Accuracy</span>
              </div>
              <p style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Tests generalization on novel scaffolds. Macro F1 = 0.7212.
              </p>
            </div>
          </div>
          <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", marginTop: "1rem", lineHeight: 1.5 }}>
            The <strong>-12.89%</strong> drop in accuracy represents a generalization gap caused by structural distribution shift (chemical out-of-distribution generalization). It is a standard result in molecular machine learning.
          </p>
        </section>

        {/* Majority-Class Baseline Section */}
        <section className="card">
          <h2 className="card-title">Majority-Class Baselines</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.5rem" }}>
            Comparison against a dummy model that always predicts the majority class (BBB+).
          </p>
          
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.9rem", borderBottom: "1px solid var(--border-color)", paddingBottom: "0.5rem" }}>
              <span>Random split majority baseline:</span>
              <strong style={{ color: "var(--text-muted)" }}>63.57% Accuracy</strong>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.9rem", borderBottom: "1px solid var(--border-color)", paddingBottom: "0.5rem" }}>
              <span>Scaffold split majority baseline:</span>
              <strong style={{ color: "var(--text-muted)" }}>60.94% Accuracy</strong>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.9rem", borderBottom: "1px solid var(--border-color)", paddingBottom: "0.5rem" }}>
              <span>Random Forest on Scaffolds:</span>
              <strong style={{ color: "var(--color-success)" }}>74.47% Accuracy</strong>
            </div>
          </div>

          <p style={{ color: "var(--text-muted)", fontSize: "0.8rem", marginTop: "1.25rem", lineHeight: 1.5 }}>
            The Random Forest classifier outperforms the scaffold majority-class baseline by <strong>+13.53%</strong> in accuracy, proving it has learned meaningful chemical patterns that generalize beyond simple class balance distributions.
          </p>
        </section>
      </div>

      {/* Model Family Comparison Table */}
      <ModelComparison />

      {/* Evaluation Figures (ROC/PR curves, confusion matrix, generalization gap) */}
      <EvaluationFigures />

      {/* Global Feature Importance (Phase 10) */}
      <GlobalImportanceChart />

      {/* Scientific Limitations Card */}
      <section className="card">
        <h2 className="card-title">
          <HelpCircle className="logo-icon" size={18} />
          Scientific Limitations & Considerations
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1rem" }}>
          Critical computational chemistry constraints of the MoleculeScope framework.
        </p>

        <div className="limitations-list">
          <div className="limitations-item">
            <span className="limitations-bullet">■</span>
            <p className="limitations-text">
              <strong>Passive Physicochemical Descriptors:</strong> The model maps structure to permeability using passive molecular descriptors (such as TPSA and LogP). Active transport mechanisms (e.g. efflux transporters like P-gp, active influx carriers) are not explicitly represented by the descriptor feature set and may contribute to errors for some compounds.
            </p>
          </div>

          <div className="limitations-item">
            <span className="limitations-bullet">■</span>
            <p className="limitations-text">
              <strong>Multi-component Mixture Predictions:</strong> Inputs containing dot-disconnected structures (e.g., salts, mixtures like `CCO.O`) have limited biological validity in these predictions, as the modeling dataset was cleaned to exclude mixtures to preserve descriptor consistency.
            </p>
          </div>

          <div className="limitations-item">
            <span className="limitations-bullet">■</span>
            <p className="limitations-text">
              <strong>Generalization Bounds:</strong> Model performance declines significantly on novel scaffolds compared to random splits. This represents a fundamental distribution shift limit. Predictions on highly exotic or novel chemical frameworks should be interpreted with caution.
            </p>
          </div>
        </div>
      </section>

      {/* Deployed Production Package Card */}
      <section className="card">
        <h2 className="card-title">Production Package Metadata</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", fontSize: "0.9rem" }}>
          <div>
            <span style={{ color: "var(--text-muted)", display: "block", fontSize: "0.8rem" }}>Production Architecture</span>
            <strong>Random Forest Classifier</strong>
          </div>
          <div>
            <span style={{ color: "var(--text-muted)", display: "block", fontSize: "0.8rem" }}>Input Features</span>
            <strong>11 Physicochemical Descriptors</strong>
          </div>
          <div>
            <span style={{ color: "var(--text-muted)", display: "block", fontSize: "0.8rem" }}>Retraining Sample Size</span>
            <strong>7,795 molecules (100% cleaned dataset)</strong>
          </div>
          <div>
            <span style={{ color: "var(--text-muted)", display: "block", fontSize: "0.8rem" }}>Model version</span>
            <strong>1.0.0 (Frozen deployment)</strong>
          </div>
        </div>
      </section>
    </div>
  );
};
