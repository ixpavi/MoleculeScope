import React, { useState } from "react";
import { ImageIcon } from "lucide-react";

interface FigureSpec {
  filename: string;
  title: string;
  caption: string;
}

const FIGURES: FigureSpec[] = [
  {
    filename: "roc_curves_scaffold.png",
    title: "ROC Curves (Scaffold Split)",
    caption: "True vs. false positive rate across all model/representation combinations on the held-out scaffold test set.",
  },
  {
    filename: "pr_curves_scaffold.png",
    title: "Precision-Recall Curves (Scaffold Split)",
    caption: "More sensitive to class imbalance than ROC-AUC; the primary ranking curve for this project.",
  },
  {
    filename: "cm_rf_descriptors_scaffold.png",
    title: "Confusion Matrix — RF + Descriptors (Scaffold)",
    caption: "The selected production architecture's confusion matrix on unseen scaffolds.",
  },
  {
    filename: "generalization_gap_macro_f1.png",
    title: "Generalization Gap (Macro F1)",
    caption: "Macro F1 drop from random split to scaffold split, by model and representation.",
  },
];

const FigureCard: React.FC<{ figure: FigureSpec; apiBaseUrl: string }> = ({ figure, apiBaseUrl }) => {
  const [failed, setFailed] = useState(false);

  return (
    <div style={{ border: "1px solid var(--border-color)", borderRadius: "8px", overflow: "hidden" }}>
      {failed ? (
        <div
          style={{
            height: "200px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "0.5rem",
            color: "var(--text-muted)",
            backgroundColor: "var(--bg-inset)",
          }}
        >
          <ImageIcon size={24} />
          <span style={{ fontSize: "0.75rem" }}>Figure unavailable</span>
        </div>
      ) : (
        <img
          src={`${apiBaseUrl}/static/figures/${figure.filename}`}
          alt={figure.title}
          onError={() => setFailed(true)}
          style={{ width: "100%", display: "block", backgroundColor: "#fff" }}
        />
      )}
      <div style={{ padding: "0.75rem" }}>
        <div style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.25rem" }}>{figure.title}</div>
        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{figure.caption}</div>
      </div>
    </div>
  );
};

export const EvaluationFigures: React.FC = () => {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

  return (
    <section className="card">
      <h2 className="card-title">Evaluation Figures</h2>
      <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.25rem" }}>
        Phase 5 evaluation plots, generated once from the saved scaffold-split predictions and served read-only.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem" }}>
        {FIGURES.map((fig) => (
          <FigureCard key={fig.filename} figure={fig} apiBaseUrl={apiBaseUrl} />
        ))}
      </div>
    </section>
  );
};
