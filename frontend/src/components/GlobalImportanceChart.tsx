import React, { useEffect, useState } from "react";
import { BarChart3 } from "lucide-react";

interface ImportanceItem {
  descriptor: string;
  importance: number;
}

export const GlobalImportanceChart: React.FC = () => {
  const [items, setItems] = useState<ImportanceItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
    fetch(`${apiBaseUrl}/api/explain/global`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load global feature importances.");
        return res.json();
      })
      .then((data) => {
        if (!Array.isArray(data?.feature_importances)) {
          throw new Error("Malformed global feature importance response.");
        }
        setItems(data.feature_importances);
      })
      .catch(() => setError("Unable to load global feature importances from the backend."));
  }, []);

  const maxImportance = items ? Math.max(...items.map((i) => i.importance)) : 1;

  return (
    <section className="card">
      <h2 className="card-title">
        <BarChart3 className="logo-icon" size={18} />
        Global Feature Importance
      </h2>
      <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "1.25rem" }}>
        Gini-based feature importances from the frozen production Random Forest classifier, ranked by
        overall contribution to prediction splits across all 7,795 training molecules.
      </p>

      {error && (
        <div className="alert alert-error" role="alert">
          <div>{error}</div>
        </div>
      )}

      {!items && !error && (
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>Loading feature importances...</p>
      )}

      {items && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
          {items.map((item) => (
            <div key={item.descriptor}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", marginBottom: "0.2rem" }}>
                <span>{item.descriptor}</span>
                <span style={{ color: "var(--text-muted)" }}>{(item.importance * 100).toFixed(1)}%</span>
              </div>
              <div className="prob-bar-bg">
                <div
                  className="prob-bar-fill bbb-plus"
                  style={{ width: `${(item.importance / maxImportance) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
};
