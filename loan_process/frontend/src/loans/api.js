import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// Create an axios instance with a base URL for loan-related API calls
const loanAPI = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

// Function to refresh the access token
const refreshAccessToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh');
    if (!refreshToken) {
      throw new Error('No refresh token found in localStorage');
    }

    const response = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
      refresh: refreshToken,
    });

    const { access } = response.data;
    localStorage.setItem('access', access);
    return access;
  } catch (error) {
    console.error('Failed to refresh access token:', error);
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.href = '/login'; // Redirect to log in if refresh fails
    throw error;
  }
};

// Add a request interceptor to include authentication token
loanAPI.interceptors.request.use(
  async (config) => {
    let token = localStorage.getItem('access');

    if (token) {
      // Decode the token to check if it has expired
      const tokenPayload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);

      if (tokenPayload.exp <= currentTime) {
        console.warn('Access token expired. Attempting to refresh...');
        token = await refreshAccessToken(); // Refresh token if expired
      }

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
  async (error) => {
    const navigate = useNavigate();

    if (error.response) {
      console.error('Response error:', error.response);

      if (error.response.status === 401) {
        console.error('Unauthorized request. Redirecting to login...');
        navigate('/login'); // Use React Router to navigate to login
      } else if (error.response.status === 403) {
        console.error('Forbidden request. You do not have access.');
        alert('You do not have permission to perform this action.');
      }
    } else if (error.request) {
      console.error('No response received:', error.request);
      alert('No response from the server. Please check your connection.');
    } else {
      console.error('Error setting up request:', error.message);
    }

    return Promise.reject(error);
  }
);

export default loanAPI;
