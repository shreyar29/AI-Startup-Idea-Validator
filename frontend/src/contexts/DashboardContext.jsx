import React, { createContext, useContext, useMemo } from 'react';

const DashboardContext = createContext(null);

export const DashboardDataProvider = ({ children, data, loading, error, requestId, retry, idea, handleExport }) => {
  // Normalize payloads safely to prevent crashes (Schema Validation Layer)
  const normalizedData = useMemo(() => {
    if (!data) return null;
    
    // Helper to guarantee an object exists, but ONLY if it was provided
    // This prevents rendering completely empty skeleton sections if the agent didn't run
    const ensureObject = (obj) => {
      if (obj === null || obj === undefined) return null;
      return typeof obj === 'object' && !Array.isArray(obj) ? obj : {};
    };
    
    return {
      ...data,
      metadata: ensureObject(data.metadata) || {},
      executive_summary: data.executive_summary || null,
      startup_score_agent: ensureObject(data.startup_score_agent),
      web_search_agent: ensureObject(data.web_search_agent),
      market_agent: ensureObject(data.market_agent),
      customer_agent: ensureObject(data.customer_agent),
      competitor_agent: ensureObject(data.competitor_agent),
      risk_agent: ensureObject(data.risk_agent),
      swot_agent: ensureObject(data.swot_agent),
      mvp_agent: ensureObject(data.mvp_agent),
      gtm_agent: ensureObject(data.gtm_agent),
      comparison_agent: ensureObject(data.comparison_agent),
    };
  }, [data]);

  const value = useMemo(() => ({
    data: normalizedData,
    loading,
    error,
    requestId,
    retry,
    idea,
    handleExport
  }), [normalizedData, loading, error, requestId, retry, idea, handleExport]);

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
};

export const useDashboardData = () => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboardData must be used within a DashboardDataProvider');
  }
  return context;
};
