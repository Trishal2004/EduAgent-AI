import api from './api';

export const courseService = {
  getAvailableCourses: async () => {
    const response = await api.get('/courses');
    return response.data;
  },
  
  getMyCourses: async () => {
    const response = await api.get('/courses/my');
    return response.data;
  },

  enroll: async (courseId) => {
    const response = await api.post(`/courses/enroll?course_id=${courseId}`);
    return response.data;
  },

  getCourseDetails: async (courseId) => {
    const response = await api.get(`/courses/${courseId}`);
    return response.data;
  },
  
  unenroll: async (courseId) => {
    const response = await api.delete(`/courses/${courseId}`);
    return response.data;
  },

  updateProgress: async (courseId, lessonId, status) => {
    const response = await api.put(`/courses/progress?course_id=${courseId}`, {
      lesson_id: lessonId,
      status: status
    });
    return response.data;
  }
};
