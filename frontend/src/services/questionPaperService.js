import api from './api';

export const questionPaperService = {
  generatePaper: async (documentId, pattern = 'university') => {
    // Route in question_papers.py is @router.post("/{document_id}/question-papers")
    // registered without prefix on api.py
    const response = await api.post(`/${documentId}/question-papers`, null, {
      params: { pattern }
    });
    return response.data;
  },

  getPapersByDocument: async (documentId) => {
    const response = await api.get(`/${documentId}/question-papers`);
    return response.data;
  },

  downloadPaper: async (paperId) => {
    // Route: /question-papers/{paper_id}/download
    // For downloads, we need to handle blobs
    const response = await api.get(`/question-papers/${paperId}/download`, {
      responseType: 'blob',
    });
    
    // Trigger download in browser
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Question_Paper_${paperId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    return true;
  }
};
