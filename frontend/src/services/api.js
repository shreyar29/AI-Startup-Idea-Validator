import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10 minutes, as validation can take time
});

export const validateIdea = async (idea, onStart, signal) => {
  const requestId = (typeof crypto !== 'undefined' && crypto.randomUUID) 
    ? crypto.randomUUID() 
    : 'req-' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
  if (onStart) {
    onStart(requestId);
  }

  try {
    const response = await api.post('/validation', null, {
      params: { query: idea },
      headers: {
        'X-Request-ID': requestId
      },
      signal
    });
    
    const jobId = response.data.job_id;
    
    // Polling Configuration
    const POLLING_INTERVAL_MS = 2000;
    const MAX_POLLING_ATTEMPTS = 180; // 6 minutes maximum limit
    const MAX_CONSECUTIVE_ERRORS = 3;
    
    let attempts = 0;
    let consecutiveErrors = 0;

    // Poll for result
    while (attempts < MAX_POLLING_ATTEMPTS) {
      if (signal?.aborted) {
        throw new Error('Request was cancelled');
      }

      await new Promise(resolve => setTimeout(resolve, POLLING_INTERVAL_MS));
      attempts++;

      try {
        const resultResponse = await api.get(`/validation/${jobId}/result`, { signal });
        
        consecutiveErrors = 0; // Reset consecutive errors on successful fetch

        if (resultResponse.data.status !== 'pending') {
          return resultResponse.data.result;
        }
      } catch (pollError) {
        if (axios.isCancel(pollError) || pollError.message === 'Request was cancelled') {
          throw pollError;
        }
        
        consecutiveErrors++;
        const isTransient = !pollError.response || pollError.response.status >= 500 || pollError.response.status === 429;
        
        if (!isTransient || consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
          throw pollError; // Bubble up if it's a fatal error or we've retried too many times
        }
      }
    }
    
    throw new Error('Validation timed out after maximum polling attempts.');
  } catch (error) {
    if (axios.isCancel(error) || error.message === 'Request was cancelled') {
      throw new Error('Validation was cancelled.');
    }
    if (error.message === 'Validation timed out after maximum polling attempts.') {
      throw error;
    }
    if (error.response) {
      const message = error.response.data?.detail || `Server error: ${error.response.status}`;
      throw new Error(message);
    } else if (error.request) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('The validation request timed out. Please try again.');
      }
      throw new Error('Network error. Please check your connection and ensure the backend is running.');
    } else {
      throw new Error(error.message || 'An unexpected error occurred while setting up the request.');
    }
  }
};

export const getReportById = async (reportId, signal) => {
  try {
    const response = await api.get(`/validation/${reportId}/result`, { signal });
    if (response.data.status === 'success' || response.data.result) {
      return response.data.result;
    }
    throw new Error('Report not found or not finished.');
  } catch (error) {
    if (axios.isCancel(error) || error.message === 'Request was cancelled') {
      throw new Error('Request was cancelled.');
    }
    throw error;
  }
};

export const saveToHistory = async (userId, idea, resultData) => {
  try {
    const response = await api.post('/history', {
      user_id: parseInt(userId, 10),
      prompt: idea,
      response_data: resultData
    });
    return response.data;
  } catch (error) {
    console.error('Failed to save to history via API:', error.message);
    throw error;
  }
};

// --- WORKSPACE APIs ---
export const getProjects = async () => {
  const response = await api.get('/api/workspace/projects');
  return response.data;
};

export const createProject = async (name, description, reportId) => {
  const response = await api.post('/api/workspace/projects', {
    name, description, report_id: reportId
  });
  return response.data;
};

export const createTask = async (taskData) => {
  const response = await api.post('/api/workspace/tasks', taskData);
  return response.data;
};

export const getTasks = async (projectId) => {
  const response = await api.get(`/api/workspace/projects/${projectId}/tasks`);
  return response.data;
};

export const updateTask = async (taskId, updates) => {
  const response = await api.patch(`/api/workspace/tasks/${taskId}`, updates);
  return response.data;
};

export default api;
