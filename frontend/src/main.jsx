import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './index.css'

// 1. Root-level resilience for uncaught global errors during early bootstrap
window.addEventListener('error', (event) => {
  console.error('[Bootstrap] Uncaught exception:', event.error?.name || 'UnknownError');
});
window.addEventListener('unhandledrejection', (event) => {
  console.error('[Bootstrap] Unhandled promise rejection:', event.reason?.name || 'UnknownReason');
});

// 2. Performance instrumentation hooks (Web Vitals)
const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && typeof onPerfEntry === 'function') {
    import('web-vitals').then(({ onCLS, onFID, onFCP, onLCP, onTTFB }) => {
      onCLS(onPerfEntry);
      onFID(onPerfEntry);
      onFCP(onPerfEntry);
      onLCP(onPerfEntry);
      onTTFB(onPerfEntry);
    }).catch(err => {
      console.warn('[Telemetry] Web vitals module not found or failed to load.', err?.name);
    });
  }
};

const bootstrapApplication = () => {
  try {
    const rootElement = document.getElementById('root');
    if (!rootElement) {
      throw new Error('Root element not found in DOM.');
    }

    const root = ReactDOM.createRoot(rootElement);
    
    root.render(
      <React.StrictMode>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </React.StrictMode>
    );

    // Optional: Log startup diagnostics in non-production environments
    if (import.meta.env.DEV) {
      console.info('[Diagnostics] Application bootstrap completed successfully.');
    }

    // Optional: Pass a logger or analytics endpoint to capture Web Vitals
    // reportWebVitals(console.log);

  } catch (error) {
    // 3. Safe error tracking without exposing sensitive internal data
    console.error('[Fatal] Application failed to bootstrap. Reason:', error.name || 'Unknown');
    
    // Fallback UI if React completely fails to mount (bypassing ErrorBoundary)
    const rootElement = document.getElementById('root');
    if (rootElement) {
      rootElement.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; padding: 2rem; font-family: system-ui, sans-serif; text-align: center; background-color: #0B0E14; color: #fff;">
          <h2 style="color: #F87171; margin-bottom: 1rem;">Application Error</h2>
          <p style="color: #9CA3AF; margin-bottom: 2rem;">The application encountered a critical error during startup.</p>
          <button onclick="window.location.reload()" style="background: #3B82F6; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 0.5rem; cursor: pointer; font-weight: 500;">Reload Page</button>
        </div>
      `;
    }
  }
};

bootstrapApplication();
