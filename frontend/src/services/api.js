import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeArticle = async (data) => {
  const response = await api.post('/api/v1/analyze', data);
  return response.data;
};

export const getHistory = async () => {
  const response = await api.get('/api/v1/history');
  return response.data;
};

export const health = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
