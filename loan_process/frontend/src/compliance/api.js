import axios from 'axios';

// Create an axios instance for compliance-related API calls
const complianceAPI = axios.create({ baseURL: '/api/' });

// Add a request interceptor to include the authentication token
complianceAPI.interceptors.request.use(
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

// Add a response interceptor for handling errors globally
complianceAPI.interceptors.response.use(
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

export default complianceAPI;