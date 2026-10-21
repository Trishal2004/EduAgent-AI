import api from './api';

export const kgService = {
  getGraph: async () => {
    const res = await api.get('/kg/graph');
    return res.data;
  },
  getTopicDetails: async (topicId) => {
    const res = await api.get(`/kg/topics/${topicId}`);
    return res.data;
  }
};
