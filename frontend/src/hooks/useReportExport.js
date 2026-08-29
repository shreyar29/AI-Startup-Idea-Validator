import { useState, useCallback } from 'react';
import { exportToPDF, exportToPPT } from '../services/exportService';

export const useReportExport = () => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState(null);

  const handleExport = useCallback(async (idea, data, format = 'pdf') => {
    if (!data) return false;
    
    setIsExporting(true);
    setExportError(null);
    
    try {
      let success = false;
      if (format === 'ppt') {
        success = await exportToPPT(idea, data);
      } else {
        success = await exportToPDF(idea, data);
      }
      
      if (!success) {
        setExportError(`${format.toUpperCase()} Export failed gracefully. Check logs.`);
      }
      return success;
    } catch (e) {
      console.error(`[useReportExport] Unexpected ${format.toUpperCase()} export error:`, e);
      setExportError(e.message || 'Export failed');
      return false;
    } finally {
      setIsExporting(false);
    }
  }, []);

  return { handleExport, isExporting, exportError };
};
