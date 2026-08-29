import axios from 'axios';
import { setAuthData } from '../utils/authUtils';

const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

export const authService = {
  async login(email, password) {
    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        username: email,
        password: password
      });
      setAuthData(response.data);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Login failed. Please try again.';
    }
  },

  async signup(name, email, password) {
    try {
      const response = await axios.post(`${API_URL}/api/auth/signup`, {
        full_name: name, // Fixed bug: Full Name is collected and now sent to the backend
        username: email,
        password: password
      });
      setAuthData(response.data);
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Signup failed. Please try again.';
    }
  }
};
