import api from './api';

export const workspaceService = {
  getWorkspaceDashboard: async () => {
    const res = await api.get('/workspace/');
    return res.data;
  }
};
