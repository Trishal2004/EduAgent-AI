import api from './api';

export const tutorService = {
  getHistory: async () => {
    const response = await api.get('/tutor/history');
    return response.data;
  },

  createSession: async () => {
    const response = await api.post('/tutor/session');
    return response.data;
  },
  
  getSession: async (sessionId) => {
    const response = await api.get(`/tutor/session/${sessionId}`);
    return response.data;
  },

  deleteSession: async (sessionId) => {
    const response = await api.delete(`/tutor/session/${sessionId}`);
    return response.data;
  },

  chat: async (sessionId, question, documentId, imageData, signal, onChunk) => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    const response = await fetch(`${API_URL}/tutor/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ session_id: sessionId, question, document_id: documentId, image_data: imageData }),
      signal
    });

    if (!response.ok) {
       if (response.status === 401) {
         localStorage.removeItem('token');
         window.location.href = '/login';
       }
       let errDetail = 'Failed to fetch';
       try { const data = await response.json(); errDetail = data.detail || errDetail; } catch (e) {}
       throw new Error(errDetail);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let finalData = null;
    let errorMsg = null;
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunkString = decoder.decode(value, { stream: true });
      const lines = chunkString.split('\n\n');
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.replace('data: ', '');
          if (!jsonStr) continue;
          try {
            const data = JSON.parse(jsonStr);
            if (data.chunk && onChunk) onChunk(data.chunk);
            if (data.done) finalData = data.response;
            if (data.error) errorMsg = data.error;
          } catch (e) {
            console.error("Parse error", e);
          }
        }
      }
    }
    
    if (errorMsg) throw new Error(errorMsg);
    return finalData;
  }
};
