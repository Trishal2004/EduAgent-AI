import api from './api';

export const dashboardService = {
  getDashboardMetrics: async () => {
    const response = await api.get('/dashboard/metrics');
    return response.data;
  },
  
  updateDashboardProfile: async (data) => {
    const response = await api.put('/dashboard/profile', data);
    return response.data;
  }
};
