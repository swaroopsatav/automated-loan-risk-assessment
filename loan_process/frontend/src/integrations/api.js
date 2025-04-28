import axios from 'axios';

const integrationsAPI = axios.create({ baseURL: '/api/' });

// Add a request interceptor to include the Authorization header if the token exists
integrationsAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Handle errors occurring during request setup
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors globally
integrationsAPI.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log the error for debugging
    console.error('API response error:', error);

    // Check if the error is due to an expired or invalid token
    if (error.response && error.response.status === 401) {
      // Optionally, handle token expiration (e.g., logout the user, refresh the token, etc.)
      console.warn('Unauthorized. Token might be expired or invalid.');
      // You can add logic to clear the token and redirect to login, e.g.:
      // localStorage.removeItem('access');
      // window.location.href = '/login';
    }

    // Pass the error to the caller
    return Promise.reject(error);
  }
);

export default integrationsAPI;