import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:8000/users_authentication';

// Create axios instance with default config
const axiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// Register user
export const registerUser = async (data) => {
  try {
    const response = await axiosInstance.post('/register/', {
      username: data.username,
      email: data.email,
      password: data.password,
      password_confirmation: data.confirmPassword
    });

    // Store tokens if registration returns them (as per your API doc)
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return {success: true, data: response.data};
  } catch (error) {
    if (error.response && error.response.data) {
      return {success: false, errors: error.response.data};
    }
    return {
      success: false,
      errors: {general: ['Network error. Please try again.']}
    };
  }
};

// Login user
export const loginUser = async (data) => {
  try {
    const response = await axiosInstance.post(
        '/login/', {username: data.username, password: data.password});

    // Store tokens on successful login
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);

      // Store basic user info (you can enhance this later)
      localStorage.setItem('user', JSON.stringify({username: data.username}));
    }

    return {success: true, data: response.data};
  } catch (error) {
    if (error.response && error.response.data) {
      return {success: false, errors: error.response.data};
    }
    return {
      success: false,
      errors: {general: ['Network error. Please try again.']}
    };
  }
};

// Refresh token
export const refreshToken = async () => {
  try {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
      throw new Error('No refresh token');
    }

    const response = await axiosInstance.post('/refresh/', {refresh: refresh});

    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
    }

    return {success: true, data: response.data};
  } catch (error) {
    // Clear everything if refresh fails
    logout();
    return {success: false, error: 'Session expired. Please login again.'};
  }
};

// Logout user
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

// Get current user
export const getCurrentUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

// Check if user is authenticated
export const isAuthenticated = () => {
  const token = localStorage.getItem('access_token');
  if (!token) return false;

  // Optional: Check if token is expired
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000;  // Convert to milliseconds
    return Date.now() < exp;
  } catch {
    return true;  // If can't decode, assume valid
  }
};

// Get auth token
export const getToken = () => {
  return localStorage.getItem('access_token');
};

// Export all functions as a service object for convenience
const AuthService = {
  registerUser,
  loginUser,
  refreshToken,
  logout,
  getCurrentUser,
  isAuthenticated,
  getToken
};

export default AuthService;