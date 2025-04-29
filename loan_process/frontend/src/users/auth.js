import API from './api';

/**
 * Logs in the user by sending credentials to the backend API.
 * Stores the access and refresh tokens in localStorage on success.
 * @param {Object} credentials - The user's login credentials containing username and password.
 * @returns {Object} - An object containing success status and message.
 */
export const loginUser = async ({username, password}) => {
    try {
        const response = await API.post('/api/users/auth/login/', {
            username,
            password
        });

        if (!response.ok) {
            return {
                success: false,
                message: response.data.detail || 'Login failed.'
            };
        }

        const {access, refresh} = response.data;

        if (access && refresh) {
            localStorage.setItem('access', access);
            localStorage.setItem('refresh', refresh);
            return {
                success: true,
                message: 'Login successful.'
            };
        } else {
            return {
                success: false,
                message: 'Invalid response: Access or refresh token missing.'
            };
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
