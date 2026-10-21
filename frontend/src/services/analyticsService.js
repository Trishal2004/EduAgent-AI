import api from './api';

export const analyticsService = {
  getDashboardMetrics: async () => {
    // Route: GET /analytics/dashboard
    const response = await api.get('/analytics/dashboard');
    return response.data;
  }
};
