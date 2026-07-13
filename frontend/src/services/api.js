import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async () => {
  const response = await api.get('/');
  return response.data;
};

export const validateStartup = async (query) => {
  try {
    const response = await api.get('/search', { params: { query } });
    return response.data;
  } catch (error) {
    // If backend returns a structured HTTP exception, surface its detail string
    if (error.response && error.response.data && error.response.data.detail) {
      throw new Error(error.response.data.detail);
    }
    // Otherwise throw the generic error
    throw error;
  }
};

export default api;
