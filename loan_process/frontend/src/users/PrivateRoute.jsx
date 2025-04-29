import React from 'react';
import { Navigate } from 'react-router-dom';

/**
 * Validates the JWT token by checking its structure and expiration.
 * @returns {boolean}
 */
const isTokenValid = () => {
  const token = localStorage.getItem('access');
  if (!token) return false;

  try {
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    const payload = JSON.parse(atob(parts[1]));
    const currentTime = Math.floor(Date.now() / 1000);

    return payload.exp && payload.exp > currentTime;
  } catch (error) {
    console.error('Error decoding or validating token:', error);
    return false;
  }
};

const PrivateRoute = ({ children }) => {
  return isTokenValid() ? children : <Navigate to="/login" replace />;
};

export default PrivateRoute;
