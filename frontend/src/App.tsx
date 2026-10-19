import { useState } from "react";
import { AppShell } from "./components/AppShell";
import { PredictorPage } from "./components/PredictorPage";
import { PerformancePage } from "./components/PerformancePage";
import { BatchScreenerPage } from "./components/BatchScreenerPage";
import { ComparePage } from "./components/ComparePage";
import { ErrorBoundary } from "./components/ErrorBoundary";

function App() {
  const [activeTab, setActiveTab] = useState<"predictor" | "compare" | "performance" | "batch">("predictor");

  return (
    <AppShell activeTab={activeTab} setActiveTab={setActiveTab}>
      <ErrorBoundary key={activeTab}>
        {activeTab === "predictor" && <PredictorPage />}
        {activeTab === "compare" && <ComparePage />}
        {activeTab === "performance" && <PerformancePage />}
        {activeTab === "batch" && <BatchScreenerPage />}
      </ErrorBoundary>
    </AppShell>
  );
}

export default App;
