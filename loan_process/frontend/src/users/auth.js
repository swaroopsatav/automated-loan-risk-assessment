import API from './api';

/**
 * Resets a user's password using a token received via email.
 * @param {string} token - The password reset token from the email link
 * @param {string} password - The new password
 * @returns {Object} - An object containing success status and message
 */
export const resetPassword = async (token, password) => {
    try {
        const response = await API.post('/api/users/auth/password-reset/confirm/', {
            token,
            password
        });

        if (response.status !== 200) {
            return {
                success: false,
                message: response.data.detail || 'Password reset failed.'
            };
        }

        return { success: true, message: 'Password has been reset successfully.' };
    } catch (err) {
        console.error('Password reset error:', err);
        return {
            success: false,
            message: err.response?.data?.detail || 'Unable to reset password. The link may be expired or invalid.'
        };
    }
};

/**
 * Changes the user's password when they are already logged in.
 * @param {string} current_password - The user's current password
 * @param {string} new_password - The new password
 * @returns {Object} - An object containing success status and message
 */
export const changePassword = async (current_password, new_password) => {
    try {
        const response = await API.post('/api/users/auth/password-change/', {
            current_password,
            new_password
        });

        if (response.status !== 200) {
            return {
                success: false,
                message: response.data.detail || 'Password change failed.'
            };
        }

        return { success: true, message: 'Password has been changed successfully.' };
    } catch (err) {
        console.error('Password change error:', err);
        return {
            success: false,
            message: err.response?.data?.detail || 'Unable to change password. Please check your current password.'
        };
    }
};

/**
 * Handles the OAuth callback by exchanging the authorization code for tokens.
 * @param {string} provider - The OAuth provider (google, linkedin, github)
 * @param {string} code - The authorization code from the OAuth provider
 * @param {string} state - The state parameter from the OAuth provider (for security)
 * @returns {Object} - An object containing success status and message
 */
export const handleOAuthCallback = async (provider, code, state) => {
    try {
        const response = await API.post(`/api/users/auth/${provider}/callback/`, {
            code,
            state
        });

        if (response.status !== 200) {
            return {
                success: false,
                message: response.data.detail || `${provider} authentication failed.`
            };
        }

        const {access, refresh} = response.data;

        if (access && refresh) {
            localStorage.setItem('access', access);
            localStorage.setItem('refresh', refresh);
            return { success: true, message: 'Authentication successful.' };
        } else {
            return { success: false, message: 'Invalid response: Access or refresh token missing.' };
        }
    } catch (err) {
        console.error(`${provider} OAuth callback error:`, err);
        return {
            success: false,
            message: err.response?.data?.detail || 'Unable to complete authentication. Please try again later.'
        };
    }
};

/**
 * Logs in the user by sending credentials to the backend API.
 * Stores the access and refresh tokens in localStorage on success.
 * @param {Object} credentials - The user's login credentials containing username and password.
 * @returns {Object} - An object containing success status and message.
 */
export const loginUser = async ({username, password}) => {
    try {
        const response = await API.post('/api/users/auth/login/', { username, password });

        if (response.status !== 200) {
            return {
                success: false,
                message: response.data.detail || 'Login failed.'
            };
        }

        const {access, refresh} = response.data;

        if (access && refresh) {
            localStorage.setItem('access', access);
            localStorage.setItem('refresh', refresh);
            return { success: true, message: 'Login successful.' };
        } else {
            return { success: false, message: 'Invalid response: Access or refresh token missing.' };
        }

    } catch (err) {
        console.error('Login error:', err);
        return {
            success: false,
            message: 'Unable to connect to the server. Please try again later.'
        };
    }
};
/**
 * Logs out the user by clearing tokens from localStorage.
 * Optionally, you can redirect the user to the login page or perform other actions.
 */
export const logoutUser = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.dispatchEvent(new Event('loginStateChanged')); // trigger login state update
};
