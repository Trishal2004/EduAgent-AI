import api from './api';

export const chatService = {
  sendMessage: async (question) => {
    const response = await api.post('/chat/', { question });
    return response.data;
  }
};
