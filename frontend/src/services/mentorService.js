import api from './api';

export const mentorService = {
  getDashboard: async () => {
    const res = await api.get('/mentor/dashboard');
    return res.data;
  },

  generateInsights: async () => {
    const res = await api.post('/mentor/generate');
    return res.data;
  },

  getChatHistory: async () => {
    const res = await api.get('/mentor/chat/history');
    return res.data;
  },

  sendChatMessage: async (message) => {
    const res = await api.post('/mentor/chat', { message });
    return res.data;
  }
};
