import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import API from './api';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setEmail(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setIsLoading(true);

        if (!email) {
            setMessage('Please enter your email address');
            setIsLoading(false);
            return;
        }

        try {
            const response = await API.post('/api/users/auth/password-reset/', { email });
            setIsSuccess(true);
            setMessage('Password reset link has been sent to your email address');
            setTimeout(() => navigate('/login'), 5000);
        } catch (err) {
            console.error('Password reset error:', err);
            setMessage(
                err.response?.data?.detail || 
                'Unable to process your request. Please try again later.'
            );
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <form 
            onSubmit={handleSubmit}
            className="p-8 max-w-md mx-auto bg-white shadow-md rounded-lg border border-gray-200"
        >
            <h2 className="text-2xl font-bold mb-4 text-center text-gray-800">FORGOT PASSWORD</h2>

            {message && (
                <p className={`text-center mb-4 border p-2 rounded-lg ${
                    isSuccess ? 'text-green-600 border-green-400 bg-green-100' : 'text-red-600 border-red-400 bg-red-100'
                }`}>
                    {message}
                </p>
            )}

            <div className="mb-4">
                <label htmlFor="email" className="block text-gray-700 mb-2">Email Address</label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    value={email}
                    onChange={handleChange}
                    placeholder="Enter your email address"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>

            <button
                type="submit"
                disabled={isLoading}
                className={`w-full px-4 py-2 rounded-lg transition duration-300 ${
                    isLoading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-500 text-white hover:bg-blue-600'
                }`}
            >
                {isLoading ? 'Processing...' : 'Reset Password'}
            </button>

            <div className="mt-4 text-center">
                <Link 
                    to="/login" 
                    className="text-blue-500 hover:text-blue-700 transition duration-300"
                >
                    Back to Login
                </Link>
            </div>
        </form>
    );
};

export default ForgotPassword;
