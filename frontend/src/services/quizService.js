import api from './api';

export const quizService = {
  generateQuiz: async (documentId, difficulty, numQuestions = 10, topic = null, sourceText = null) => {
    const res = await api.post(`/quiz/generate`, {
      document_id: documentId,
      difficulty: difficulty,
      number_of_questions: numQuestions,
      topic: topic,
      source_text: sourceText
    });
    return res.data;
  },

  getQuiz: async (quizId) => {
    const res = await api.get(`/quizzes/${quizId}`);
    return res.data;
  },

  submitQuiz: async (quizId, answers, timeSpent = 0) => {
    const res = await api.post(`/quizzes/${quizId}/submit`, { answers, time_spent_seconds: timeSpent });
    return res.data;
  },

  getQuizHistory: async () => {
    const res = await api.get('/quizzes/history');
    return res.data;
  },
  
  getQuizResults: async (quizId) => {
    const res = await api.get(`/quizzes/${quizId}/results`);
    return res.data;
  },
  
  getQuizzes: async () => {
    const res = await api.get('/quizzes');
    return res.data;
  },

  getDailyQuizzes: async () => {
    const res = await api.get('/quizzes/daily');
    return res.data;
  },

  generateDailyQuizzes: async () => {
    const res = await api.post('/quizzes/daily/generate');
    return res.data;
  },

  startQuiz: async (quizId) => {
    const res = await api.post(`/quizzes/${quizId}/start`);
    return res.data;
  }
};
