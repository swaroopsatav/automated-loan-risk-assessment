import axios from 'axios';

// Create an axios instance with a base URL for loan-related API calls
const loanAPI = axios.create({
  baseURL: 'http://localhost:8000/',
});

// Add a request interceptor to include authentication token
loanAPI.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access');
    if (token) {
      // Optionally check if token is expired
      const expiry = localStorage.getItem('token_expiry');
      if (expiry && Date.now() > parseInt(expiry)) {
        console.warn('Token expired');
        // Handle token expiration (e.g., redirect to login or refresh token)
        window.location.href = '/login';
      } else {
        config.headers.Authorization = `Bearer ${token}`;
      }
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
        // You could display a message to the user here before redirecting
        window.location.href = '/login';
      } else if (error.response.status === 500) {
        console.error('Server error. Please try again later.');
        // Optionally, show a notification or alert to the user
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
