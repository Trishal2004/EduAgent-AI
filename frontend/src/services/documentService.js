import api from './api';

export const documentService = {
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    // Using api instance which already has interceptors for auth
    const res = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  processDocument: async (documentId) => {
    const res = await api.post(`/documents/${documentId}/process`);
    return res.data;
  },

  getDocuments: async () => {
    const res = await api.get('/documents/');
    return res.data;
  },

  deleteDocument: async (documentId) => {
    const res = await api.delete(`/documents/${documentId}`);
    return res.data;
  },

  renameDocument: async (documentId, newName) => {
    const res = await api.put(`/documents/${documentId}/rename`, { new_name: newName });
    return res.data;
  },
  
  getDownloadUrl: (documentId) => {
    // Return the full URL for downloading since we might just want to use a regular anchor tag or window.open
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/documents/${documentId}/download`;
  }
};
