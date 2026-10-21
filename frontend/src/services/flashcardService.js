import api from './api';

export const flashcardService = {
  generateFlashcards: async (documentId, numCards = 15) => {
    const response = await api.post(`/documents/${documentId}/flashcards`, null, {
      params: { num_cards: numCards }
    });
    return response.data;
  },

  generateFlashcardsFromTopic: async (documentId, topic, sourceText, numCards = 10) => {
    const response = await api.post(`/documents/flashcards/generate`, {
      document_id: documentId,
      topic: topic,
      source_text: sourceText,
      num_cards: numCards
    });
    return response.data;
  },

  getFlashcardDecksByDocument: async (documentId) => {
    const response = await api.get(`/documents/${documentId}/flashcards`);
    return response.data;
  },

  getFlashcardDeck: async (deckId) => {
    // router prefix is /documents, path is /flashcards/decks/{deck_id}
    const response = await api.get(`/documents/flashcards/decks/${deckId}`);
    return response.data;
  }
};
