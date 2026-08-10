import { useState } from "react";
import { AppShell } from "./components/AppShell";
import { PredictorPage } from "./components/PredictorPage";
import { PerformancePage } from "./components/PerformancePage";
import { BatchScreenerPage } from "./components/BatchScreenerPage";
import { ErrorBoundary } from "./components/ErrorBoundary";

function App() {
  const [activeTab, setActiveTab] = useState<"predictor" | "performance" | "batch">("predictor");

  return (
    <AppShell activeTab={activeTab} setActiveTab={setActiveTab}>
      <ErrorBoundary key={activeTab}>
        {activeTab === "predictor" && <PredictorPage />}
        {activeTab === "performance" && <PerformancePage />}
        {activeTab === "batch" && <BatchScreenerPage />}
      </ErrorBoundary>
    </AppShell>
  );
}

export default App;
