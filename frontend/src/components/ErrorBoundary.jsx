import React from 'react';
import { AlertTriangle } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="glass-panel p-6 rounded-2xl border-error/20 bg-error/5 flex flex-col items-center justify-center text-center">
          <AlertTriangle className="w-8 h-8 text-error mb-3" />
          <h3 className="text-lg font-bold text-error">Failed to load this section</h3>
          <p className="text-sm text-textMuted mt-1">There was a rendering error in this module. Other sections remain functional.</p>
          <button 
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 px-4 py-2 bg-surface border border-border/50 text-sm font-medium rounded-lg hover:bg-surface/80 transition-colors"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children; 
  }
}

export default ErrorBoundary;
