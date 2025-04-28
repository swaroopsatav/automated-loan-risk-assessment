import axios from 'axios';

// Create an axios instance with a base URL
const scoreApi = axios.create({
  baseURL: '/api/',
});

// Add a request interceptor for including the authentication token
scoreApi.interceptors.request.use(
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
    // Handle errors before the request is sent
    console.error('Error in request:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor for handling responses globally
scoreApi.interceptors.response.use(
  (response) => {
    // Handle successful responses
    return response;
  },
  (error) => {
    // Handle errors globally
    if (error.response) {
      console.error('Response error:', error.response);
      if (error.response.status === 401) {
        // Handle token expiration or unauthorized access
        console.error('Unauthorized request. Redirecting to login...');
        window.location.href = '/login'; // Redirect to login page
      }
    } else if (error.request) {
      // Handle errors where no response was received
      console.error('No response received:', error.request);
    } else {
      // Handle other types of errors
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

export default scoreApi;