import axios from 'axios';

// Create a centralized Axios instance
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token to every request automatically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle global errors (like 401 Unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Unauthorized! Redirecting to login or clearing token...");
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    // Extract a readable error message from the backend if available
    let message = 'An unexpected error occurred.';
    if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        message = error.response.data.detail.map(err => err.msg).join(', ');
        // Overwrite the detail so frontend components using it won't crash
        error.response.data.detail = message;
      } else {
        message = error.response.data.detail;
      }
    } else if (error.message) {
      message = error.message;
    }
    
    error.customMessage = message;
    
    return Promise.reject(error);
  }
);

export default api;
