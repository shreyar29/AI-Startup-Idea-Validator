export const exportToPDF = async (idea, data) => {
  const token = localStorage.getItem('token');
  
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000')}/api/export/pdf`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        startup_idea: idea || (data?.metadata?.startup_idea) || 'Unknown Idea',
        analysis_payload: data,
        validation_score: data?.startup_score_agent?.overall_score || 0
      })
    });
    
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'VentureLens_Investor_Report.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      return true;
    } else {
      console.error('Export failed via API');
      return false;
    }
  } catch (err) {
    console.error('Export failed via API', err);
    return false;
  }
};
