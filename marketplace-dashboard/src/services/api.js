import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Authorization': 'Bearer test-token'
  }
});

export const getRecommendations = async (productId) => {
  try {
    const response = await api.get(`/products/${productId}/recommendations`);
    return response.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
};

export const getCategoryDistribution = async () => {
  try {
    const response = await api.get('/metrics/category_distribution');
    return response.data;
  } catch (error) {
    console.error('Error fetching category distribution:', error);
    throw error;
  }
};