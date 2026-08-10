import { Atom, FileSpreadsheet, Gauge } from "lucide-react";
import { Logo } from "./Logo";

type Tab = "predictor" | "performance" | "batch";

interface AppShellProps {
  children: React.ReactNode;
  activeTab: Tab;
  setActiveTab: (tab: Tab) => void;
}

const NAV_ITEMS: { tab: Tab; label: string; meta?: string; icon: typeof Atom }[] = [
  { tab: "predictor", label: "Predictor", icon: Atom },
  { tab: "batch", label: "Batch screener", meta: "CSV", icon: FileSpreadsheet },
  { tab: "performance", label: "Performance", icon: Gauge },
];

export const AppShell: React.FC<AppShellProps> = ({
  children,
  activeTab,
  setActiveTab,
}) => {
  return (
    <div className="shell">
      {/* Sidebar rail — collapsed to icons, expands on hover */}
      <aside className="rail">
        <div className="rail-inner">
          <div className="brand">
            <Logo size={26} />
            <span className="brand-name">MoleculeScope</span>
          </div>

          <nav className="nav">
            {NAV_ITEMS.map(({ tab, label, meta, icon: Icon }) => (
              <button
                key={tab}
                type="button"
                className={`nav-item ${activeTab === tab ? "active" : ""}`}
                onClick={() => setActiveTab(tab)}
                title={label}
              >
                <span className="nav-icon">
                  <Icon size={18} />
                </span>
                <span className="nav-label">{label}</span>
                {meta && <span className="meta">{meta}</span>}
              </button>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main panel */}
      <main className="main">
        <header className="mobile-header">
          <div className="brand">
            <Logo size={24} />
            <span className="brand-name" style={{ fontSize: "17px" }}>MoleculeScope</span>
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {NAV_ITEMS.map(({ tab, label, icon: Icon }) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className="example-btn"
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  borderColor: activeTab === tab ? "var(--accent)" : undefined,
                  color: activeTab === tab ? "var(--accent)" : undefined,
                }}
              >
                <Icon size={14} />
                {label === "Batch screener" ? "Batch" : label}
              </button>
            ))}
          </div>
        </header>

        {children}
      </main>
    </div>
  );
};
