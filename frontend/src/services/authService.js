import api from './api';

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', {
      email: email,
      password: password
    });
    return response.data;
  },

  loginRequest: async (email, password) => {
    const response = await api.post('/auth/login-request', { email, password });
    return response.data;
  },

  verifyLoginOtp: async (email, otp) => {
    const response = await api.post('/auth/verify-otp', { email, otp });
    return response.data;
  },
  
  register: async (email, password, passwordConfirm, fullName) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      password_confirm: passwordConfirm,
      full_name: fullName
    });
    return response.data;
  },
  
  verifyEmail: async (email, otp) => {
    const response = await api.post('/auth/verify-email', { email, otp });
    return response.data;
  },
  
  resendOtp: async (email) => {
    const response = await api.post('/auth/resend-otp', { email });
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  forgotPassword: async (email) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },
  
  resetPassword: async (email, otp, newPassword, confirmPassword) => {
    const response = await api.post('/auth/reset-password', {
      email,
      otp,
      new_password: newPassword,
      confirm_password: confirmPassword
    });
    return response.data;
  },
  
  updateProfile: async (data) => {
    const response = await api.put('/auth/me', data);
    return response.data;
  },
  
  changePassword: async (current_password, new_password, confirm_password) => {
    const response = await api.put('/auth/password', {
      current_password, new_password, confirm_password
    });
    return response.data;
  },

  deleteAccount: async () => {
    const response = await api.delete('/auth/me');
    return response.data;
  }
};
