import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { handleOAuthCallback } from './auth';

/**
 * Component to handle OAuth callback
 * This component is rendered when the user is redirected back from the OAuth provider
 * It extracts the authorization code and state from the URL and exchanges them for tokens
 */
const OAuthCallback = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [status, setStatus] = useState('Processing authentication...');
  const [error, setError] = useState('');

  useEffect(() => {
    const processOAuthCallback = async () => {
      try {
        // Extract the query parameters from the URL
        const searchParams = new URLSearchParams(location.search);
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');
        
        // Get the provider from the pathname (e.g., /auth/google/callback -> google)
        const pathParts = location.pathname.split('/');
        const provider = pathParts[pathParts.length - 2]; // Assuming path is like /auth/[provider]/callback
        
        if (error) {
          setError(`Authentication failed: ${error}`);
          setStatus('Authentication failed');
          return;
        }
        
        if (!code) {
          setError('No authorization code received');
          setStatus('Authentication failed');
          return;
        }
        
        // Exchange the code for tokens
        const result = await handleOAuthCallback(provider, code, state);
        
        if (result.success) {
          setStatus('Authentication successful! Redirecting...');
          
          // Trigger login state update
          window.dispatchEvent(new Event('loginStateChanged'));
          
          // Redirect to the saved redirect URL or default to profile
          const redirectUrl = localStorage.getItem('oauth_redirect_url') || '/profile';
          localStorage.removeItem('oauth_redirect_url'); // Clean up
          
          // Redirect after a short delay to show the success message
          setTimeout(() => navigate(redirectUrl), 1500);
        } else {
          setError(result.message);
          setStatus('Authentication failed');
        }
      } catch (err) {
        console.error('OAuth callback processing error:', err);
        setError('An unexpected error occurred during authentication');
        setStatus('Authentication failed');
      }
    };
    
    processOAuthCallback();
  }, [location, navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
        <h2 className="text-2xl font-bold mb-4">{status}</h2>
        
        {error ? (
          <div className="text-red-600 mb-4 border border-red-400 bg-red-100 p-3 rounded-lg">
            {error}
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
          </div>
        )}
        
        {error && (
          <button
            onClick={() => navigate('/login')}
            className="mt-4 px-4 py-2 bg-indigo-500 text-white rounded hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            Back to Login
          </button>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback;