import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10 minutes, as validation can take time
});

export const validateIdea = async (idea, onStart) => {
  const requestId = (typeof crypto !== 'undefined' && crypto.randomUUID) 
    ? crypto.randomUUID() 
    : 'req-' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
  if (onStart) {
    onStart(requestId);
  }

  try {
    const response = await api.get('/search', {
      params: { query: idea },
      headers: {
        'X-Request-ID': requestId
      }
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      const message = error.response.data?.detail || `Server error: ${error.response.status}`;
      throw new Error(message);
    } else if (error.request) {
      if (error.code === 'ECONNABORTED') {
        throw new Error('The validation request timed out. Please try again.');
      }
      throw new Error('Network error. Please check your connection and ensure the backend is running.');
    } else {
      throw new Error('An unexpected error occurred while setting up the request.');
    }
  }
};

export default api;
