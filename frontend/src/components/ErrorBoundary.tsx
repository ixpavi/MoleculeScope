import React from "react";
import { AlertOctagon } from "lucide-react";

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("MoleculeScope UI crashed:", error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ error: null });
  };

  render() {
    if (this.state.error) {
      return (
        <div className="card alert-error" style={{ margin: "2rem", display: "flex", gap: "1rem", alignItems: "flex-start" }}>
          <AlertOctagon size={24} style={{ flexShrink: 0 }} />
          <div>
            <strong style={{ display: "block", marginBottom: "0.4rem" }}>Something went wrong in the UI.</strong>
            <p style={{ fontSize: "0.85rem", marginBottom: "0.75rem" }}>
              This is a frontend rendering error, not a prediction result — no molecule data was affected. Try
              reloading the page; if it keeps happening, check the browser console for details.
            </p>
            <button type="button" className="example-btn" onClick={this.handleReset}>
              Try again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
