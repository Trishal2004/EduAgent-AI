import api from './api';

export const noteService = {
  // Folders
  getFolders: async () => {
    const res = await api.get('/notes/folders');
    return res.data;
  },
  createFolder: async (name) => {
    const res = await api.post('/notes/folders', { name });
    return res.data;
  },
  deleteFolder: async (id) => {
    const res = await api.delete(`/notes/folders/${id}`);
    return res.data;
  },

  // Tags
  getTags: async () => {
    const res = await api.get('/notes/tags');
    return res.data;
  },
  createTag: async (name) => {
    const res = await api.post('/notes/tags', { name });
    return res.data;
  },
  deleteTag: async (id) => {
    const res = await api.delete(`/notes/tags/${id}`);
    return res.data;
  },

  // Notes
  getNotes: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.folder_id) params.append('folder_id', filters.folder_id);
    if (filters.tag_id) params.append('tag_id', filters.tag_id);
    if (filters.is_favorite !== undefined) params.append('is_favorite', filters.is_favorite);
    if (filters.search) params.append('search', filters.search);
    
    const res = await api.get(`/notes?${params.toString()}`);
    return res.data;
  },
  getNote: async (id) => {
    const res = await api.get(`/notes/${id}`);
    return res.data;
  },
  createNote: async (data) => {
    const res = await api.post('/notes/', data);
    return res.data;
  },
  updateNote: async (id, data) => {
    const res = await api.put(`/notes/${id}`, data);
    return res.data;
  },
  deleteNote: async (id) => {
    const res = await api.delete(`/notes/${id}`);
    return res.data;
  },
  toggleFavorite: async (id) => {
    const res = await api.post(`/notes/${id}/favorite`);
    return res.data;
  },
  generateNote: async (data) => {
    const res = await api.post('/notes/generate', data);
    return res.data;
  },
  getDocumentNotes: async (documentId) => {
    const res = await api.get(`/notes/documents/${documentId}`);
    return res.data;
  }
};
