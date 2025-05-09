import React from 'react';
import { useNavigate } from 'react-router-dom';
import API from './api';
import { AUTH_CONFIG } from '../config';

/**
 * Component for OAuth authentication buttons
 * @param {Object} props - Component props
 * @param {string} props.redirectUrl - URL to redirect after successful authentication
 * @param {string} props.buttonText - Custom text for the buttons (optional)
 * @param {string} props.className - Additional CSS classes (optional)
 * @returns {JSX.Element} - Rendered component
 */
const OAuthButtons = ({ 
  redirectUrl = AUTH_CONFIG.profileUrl, 
  buttonText = {
    google: 'Continue with Google',
    linkedin: 'Continue with LinkedIn',
    github: 'Continue with GitHub'
  },
  className = ''
}) => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = React.useState({
    google: false,
    linkedin: false,
    github: false
  });
  const [error, setError] = React.useState('');

  const handleOAuthLogin = async (provider) => {
    setError('');
    setIsLoading(prev => ({ ...prev, [provider]: true }));

    try {
      // Get the OAuth URL from the backend
      const response = await API.get(`/api/users/auth/${provider}/`);

      if (response.data && response.data.authorization_url) {
        // Store the redirect URL in localStorage to use after OAuth callback
        localStorage.setItem('oauth_redirect_url', redirectUrl);

        // Redirect to the OAuth provider's authorization page
        window.location.href = response.data.authorization_url;
      } else {
        setError(`Failed to get ${provider} authorization URL`);
      }
    } catch (err) {
      console.error(`${provider} OAuth error:`, err);
      setError(err.response?.data?.detail || `${provider} authentication failed`);
    } finally {
      setIsLoading(prev => ({ ...prev, [provider]: false }));
    }
  };

  return (
    <div className={`oauth-buttons ${className}`}>
      {error && (
        <p className="text-red-600 text-center mb-4 border border-red-400 bg-red-100 p-2 rounded-lg">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={() => handleOAuthLogin('google')}
        disabled={isLoading.google}
        className={`w-full mb-2 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
          isLoading.google ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <g transform="matrix(1, 0, 0, 1, 27.009001, -39.238998)">
            <path fill="#4285F4" d="M -3.264 51.509 C -3.264 50.719 -3.334 49.969 -3.454 49.239 L -14.754 49.239 L -14.754 53.749 L -8.284 53.749 C -8.574 55.229 -9.424 56.479 -10.684 57.329 L -10.684 60.329 L -6.824 60.329 C -4.564 58.239 -3.264 55.159 -3.264 51.509 Z"/>
            <path fill="#34A853" d="M -14.754 63.239 C -11.514 63.239 -8.804 62.159 -6.824 60.329 L -10.684 57.329 C -11.764 58.049 -13.134 58.489 -14.754 58.489 C -17.884 58.489 -20.534 56.379 -21.484 53.529 L -25.464 53.529 L -25.464 56.619 C -23.494 60.539 -19.444 63.239 -14.754 63.239 Z"/>
            <path fill="#FBBC05" d="M -21.484 53.529 C -21.734 52.809 -21.864 52.039 -21.864 51.239 C -21.864 50.439 -21.724 49.669 -21.484 48.949 L -21.484 45.859 L -25.464 45.859 C -26.284 47.479 -26.754 49.299 -26.754 51.239 C -26.754 53.179 -26.284 54.999 -25.464 56.619 L -21.484 53.529 Z"/>
            <path fill="#EA4335" d="M -14.754 43.989 C -12.984 43.989 -11.404 44.599 -10.154 45.789 L -6.734 42.369 C -8.804 40.429 -11.514 39.239 -14.754 39.239 C -19.444 39.239 -23.494 41.939 -25.464 45.859 L -21.484 48.949 C -20.534 46.099 -17.884 43.989 -14.754 43.989 Z"/>
          </g>
        </svg>
        {isLoading.google ? 'Connecting...' : buttonText.google}
      </button>

      <button
        type="button"
        onClick={() => handleOAuthLogin('linkedin')}
        disabled={isLoading.linkedin}
        className={`w-full mb-2 flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
          isLoading.linkedin ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        <svg className="h-5 w-5 mr-2" fill="#0A66C2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
        {isLoading.linkedin ? 'Connecting...' : buttonText.linkedin}
      </button>

      <button
        type="button"
        onClick={() => handleOAuthLogin('github')}
        disabled={isLoading.github}
        className={`w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
          isLoading.github ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
        </svg>
        {isLoading.github ? 'Connecting...' : buttonText.github}
      </button>

      <div className="mt-4 text-center text-sm text-gray-500">
        By continuing, you agree to our Terms of Service and Privacy Policy
      </div>
    </div>
  );
};

export default OAuthButtons;
