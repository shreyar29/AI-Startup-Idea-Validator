import React, { useRef } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

const ErrorState = ({ message, onRetry }) => {
  const isRetrying = useRef(false);

  const handleRetry = async (e) => {
    if (isRetrying.current || !onRetry) return;
    isRetrying.current = true;
    try {
      await onRetry(e);
    } finally {
      // Prevent immediate double-clicks even if onRetry is completely synchronous
      setTimeout(() => {
        isRetrying.current = false;
      }, 500);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[60vh] px-4">
      <div 
        className="glass-panel p-8 rounded-2xl max-w-md mx-auto w-full text-center"
        role="alert"
        aria-live="assertive"
      >
        <div className="bg-error/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
          <AlertTriangle className="w-8 h-8 text-error" />
        </div>
        <h3 className="text-xl font-semibold text-textMain mb-2">Validation Failed</h3>
        <p className="text-textMuted mb-8 break-words">{message}</p>
        
        {onRetry && (
          <button 
            type="button"
            onClick={handleRetry}
            className="inline-flex items-center gap-2 bg-surface hover:bg-surface/80 border border-border text-textMain px-6 py-2.5 rounded-lg font-medium transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Try Again</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorState;
