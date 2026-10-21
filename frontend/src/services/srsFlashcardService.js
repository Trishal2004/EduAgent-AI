import api from './api';

export const srsFlashcardService = {
  getDecks: async () => {
    const res = await api.get('/srs/decks');
    return res.data;
  },
  createDeck: async (data) => {
    const res = await api.post('/srs/decks', data);
    return res.data;
  },
  deleteDeck: async (deckId) => {
    const res = await api.delete(`/srs/decks/${deckId}`);
    return res.data;
  },
  updateDeck: async (deckId, data) => {
    const res = await api.put(`/srs/decks/${deckId}`, data);
    return res.data;
  },
  addCard: async (deckId, data) => {
    const res = await api.post(`/srs/decks/${deckId}/cards`, data);
    return res.data;
  },
  deleteCard: async (cardId) => {
    const res = await api.delete(`/srs/cards/${cardId}`);
    return res.data;
  },
  getDueCards: async (deckId) => {
    const res = await api.get(`/srs/decks/${deckId}/review`);
    return res.data;
  },
  saveScore: async (cardId, quality) => {
    const res = await api.post(`/srs/cards/${cardId}/review`, { quality });
    return res.data;
  },
  generateDeck: async (data) => {
    const res = await api.post('/srs/decks/generate', data);
    return res.data;
  }
};
