import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
axiosInstance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    });

// Response interceptor for token refresh
axiosInstance.interceptors.response.use(
    (response) => response, async (error) => {
      const originalRequest = error.config;

      // If error is 401 and we haven't tried to refresh yet
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        try {
          const refreshToken = localStorage.getItem('refresh_token');

          if (!refreshToken) {
            // No refresh token, redirect to login
            localStorage.clear();
            window.location.href = '/login';
            return Promise.reject(error);
          }

          // Call refresh token endpoint
          const response = await axios.post(
              'http://127.0.0.1:8000/users_authentication/refresh/',
              {refresh: refreshToken},
              {headers: {'Content-Type': 'application/json'}});

          if (response.data.access) {
            // Store new access token
            localStorage.setItem('access_token', response.data.access);

            // Update authorization header
            axiosInstance.defaults.headers.common['Authorization'] =
                `Bearer ${response.data.access}`;
            originalRequest.headers.Authorization =
                `Bearer ${response.data.access}`;

            // Retry original request
            return axiosInstance(originalRequest);
          }
        } catch (refreshError) {
          // Refresh failed - clear storage and redirect to login
          localStorage.clear();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    });

export default axiosInstance;