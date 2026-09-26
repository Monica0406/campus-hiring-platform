import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach Bearer token and normalize relative URLs
apiClient.interceptors.request.use(
  (config) => {
    if (config.url && config.url.startsWith('/api/')) {
      config.url = config.url.substring(4);
    }
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 and attempt automatic token refresh
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Do not attempt refresh on login or refresh endpoints
    const isAuthEndpoint =
      originalRequest.url?.includes('/auth/login/') ||
      originalRequest.url?.includes('/auth/refresh/') ||
      originalRequest.url?.includes('/auth/register/');

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        isRefreshing = false;
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(`${baseURL}/auth/refresh/`, {
          refresh: refreshToken,
        });

        const newAccessToken = response.data?.data?.access;
        if (newAccessToken) {
          localStorage.setItem('access_token', newAccessToken);
          apiClient.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
          processQueue(null, newAccessToken);
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');
        window.dispatchEvent(new Event('auth:logout'));
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Extracts a clear human-readable error string from backend response.
 */
export const getErrorMessage = (error, defaultMessage = 'An unexpected error occurred.') => {
  if (!error) return defaultMessage;
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (typeof error.response?.data === 'string') {
    return error.response.data;
  }
  if (error.message) {
    return error.message;
  }
  return defaultMessage;
};

export default apiClient;
