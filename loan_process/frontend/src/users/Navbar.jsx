import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logoutUser } from './auth';

const Navbar = () => {
    const navigate = useNavigate();
    const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('access'));

    // Listen for login/logout across tabs and same tab
    useEffect(() => {
        const syncLoginState = () => {
            setIsLoggedIn(!!localStorage.getItem('access'));
        };

        // Custom event for same-tab updates
        window.addEventListener('loginStateChanged', syncLoginState);

        // Native storage event for cross-tab updates
        window.addEventListener('storage', syncLoginState);

        return () => {
            window.removeEventListener('loginStateChanged', syncLoginState);
            window.removeEventListener('storage', syncLoginState);
        };
    }, []);

    const handleLogout = () => {
        const confirmLogout = window.confirm('Are you sure you want to log out?');
        if (confirmLogout) {
            try {
                logoutUser(); // Clear localStorage
                // Trigger UI updates
                window.dispatchEvent(new Event('loginStateChanged'));
                navigate('/login');
            } catch (error) {
                console.error('Logout failed:', error);
                alert('Something went wrong. Please try again.');
            }
        }
    };

    return (
        <nav className="bg-gray-800 text-white p-4 flex items-center gap-4">
            <Link to="/" className="hover:text-blue-300 transition duration-300">
                Home
            </Link>
            {!isLoggedIn ? (
                <>
                    <Link to="/register" className="hover:text-blue-300 transition duration-300">
                        Register
                    </Link>
                    <Link to="/login" className="hover:text-blue-300 transition duration-300">
                        Login
                    </Link>
                </>
            ) : (
                <>
                    <Link to="/profile" className="hover:text-blue-300 transition duration-300">
                        Profile
                    </Link>
                    <button
                        onClick={handleLogout}
                        className="ml-auto text-red-400 hover:text-red-600 transition duration-300"
                        aria-label="Logout"
                    >
                        Logout
                    </button>
                </>
            )}
        </nav>
    );
};

export default Navbar;
