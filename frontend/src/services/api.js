import axios from 'axios';

const API = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000' });

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await API.post('/api/documents/upload', formData);
  return response.data;
};

export const getDocument = async (documentId) => (await API.get(`/api/documents/${documentId}`)).data;
export default API;