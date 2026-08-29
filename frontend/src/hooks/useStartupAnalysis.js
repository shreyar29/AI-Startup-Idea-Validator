import { useState, useEffect, useRef, useCallback } from 'react';
import { validateIdea, getReportById, saveToHistory } from '../services/api';
import { storageService } from '../services/storageService';

// Simple in-memory cache for reports
const reportCache = new Map();

export const useStartupAnalysis = (idea, reportId) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentRequestId, setCurrentRequestId] = useState(reportId || null);
  
  const abortControllerRef = useRef(null);

  const fetchAnalysis = useCallback(async (isRetry = false) => {
    // Return cached data if available and we are not forcing a retry
    const cacheKey = reportId || idea;
    if (!isRetry && cacheKey && reportCache.has(cacheKey)) {
      const cached = reportCache.get(cacheKey);
      setData(cached);
      setCurrentRequestId(reportId || cached?.metadata?.correlation_id || cached?.metadata?.request_id);
      setLoading(false);
      return;
    }

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setLoading(true);
    setError(null);

    try {
      let result;
      
      if (reportId && !isRetry && !idea) {
        setCurrentRequestId(reportId);
        result = await getReportById(reportId, signal);
      } else if (idea) {
        result = await validateIdea(idea, (id) => {
          setCurrentRequestId(id);
          storageService.setActiveReportId(id);
        }, signal);
        
        const userId = storageService.getUserId();
        if (userId) {
          try {
            await saveToHistory(userId, idea, result);
          } catch (e) {
            console.error('[useStartupAnalysis] Failed to sync session with history:', e.name);
          }
        }
      } else {
        throw new Error('No idea or report ID provided.');
      }
      
      if (result?.metadata) {
        const idToSave = result.metadata.correlation_id || result.metadata.request_id || cacheKey;
        setCurrentRequestId(idToSave);
        storageService.setActiveReportId(idToSave);
      }
      
      if (!result || typeof result !== 'object') {
        throw new Error('Invalid analysis payload received from server.');
      }
      
      // Save to cache
      if (cacheKey) {
        reportCache.set(cacheKey, result);
        if (result.metadata?.correlation_id) {
          reportCache.set(result.metadata.correlation_id, result);
        }
        if (result.metadata?.request_id) {
          reportCache.set(result.metadata.request_id, result);
        }
      }
      
      setData(result);
    } catch (err) {
      const isCancelled = err.message === 'Request was cancelled.' || 
                          err.message === 'Validation was cancelled.' || 
                          (err.name === 'CanceledError');
                          
      if (!isCancelled) {
        console.error('[useStartupAnalysis] Fetch error:', err);
        const detailedError = err.message ? err.message : (typeof err === 'object' ? JSON.stringify(err) : String(err));
        setError(detailedError || 'Validation failed');
      }
    } finally {
      if (!signal.aborted) {
        setLoading(false);
      }
    }
  }, [idea, reportId]);

  useEffect(() => {
    fetchAnalysis();
    
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchAnalysis]);

  const retry = useCallback(() => {
    fetchAnalysis(true);
  }, [fetchAnalysis]);

  return { data, loading, error, requestId: currentRequestId, retry };
};
