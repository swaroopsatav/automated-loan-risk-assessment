import axios from 'axios';

// Create an axios instance with a base URL for loan-related API calls
const loanAPI = axios.create({
  baseURL: '/api/',
});

// Add a request interceptor to include authentication token
loanAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.warn('No access token found in localStorage');
    }
    return config;
  },
  (error) => {
    console.error('Error in request setup:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors globally
loanAPI.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('Response error:', error.response);
      if (error.response.status === 401) {
        console.error('Unauthorized request. Redirecting to login...');
        window.location.href = '/login';
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
    } else {
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

export default loanAPI;