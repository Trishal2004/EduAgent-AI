import api from './api';

export const plannerService = {
  getPlan: async () => {
    const response = await api.get('/planner');
    return response.data;
  },
  generatePlan: async (data) => {
    const response = await api.post('/planner/generate', data);
    return response.data;
  }
};
