import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 600000, // 10 minutes, as validation can take time
});

export const validateIdea = async (idea) => {
  const response = await api.get('/search', {
    params: { query: idea }
  });
  return response.data;
};

export default api;
