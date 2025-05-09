import React, {useState} from 'react';
import {loginUser} from './auth';
import {useNavigate, Link} from 'react-router-dom';
import {AUTH_CONFIG} from '../config';
import OAuthButtons from './OAuthButtons';

const LoginForm = () => {
    const [form, setForm] = useState({username: '', password: ''});
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const {name, value} = e.target;
        setForm((prevState) => ({...prevState, [name]: value}));
    };

    const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!form.username || !form.password) {
        setError('Please enter both username and password');
        setIsLoading(false);
        return;
    }

    try {
        const response = await loginUser({
            username: form.username.trim(),
            password: form.password
        });
        if (response.success) {
            window.dispatchEvent(new Event('loginStateChanged'));
            navigate(AUTH_CONFIG.profileUrl);
        } else {
            setError(response.message || 'Invalid credentials');
        }
    } catch (err) {
        console.error('Login error:', err);
        setError(err.response?.data?.detail || err.message || 'Unable to connect to the server. Please try again later.');
    } finally {
        setIsLoading(false);
    }
};

    return (
        <form
            onSubmit={handleSubmit}
            className="p-8 max-w-md mx-auto bg-white shadow-md rounded-lg border border-gray-200"
        >
            <h2 className="text-2xl font-bold mb-4 text-center text-gray-800">LOGIN</h2>
            {error && (
                <p className="text-red-600 text-center mb-4 border border-red-400 bg-red-100 p-2 rounded-lg">
                    {error}
                </p>
            )}
            <div className="mb-4">
                <input
                    type="text"
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    placeholder="Username"
                    required
                    autoComplete="username"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>
            <div className="mb-4">
                <input
                    type="password"
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Password"
                    required
                    autoComplete="current-password"
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
                {isLoading ? 'Logging in...' : 'Login'}
            </button>

            <div className="mt-4 text-center">
                <Link 
                    to="/forgot-password" 
                    className="text-blue-500 hover:text-blue-700 transition duration-300"
                >
                    Forgot Password?
                </Link>
            </div>

            <div className="my-6 flex items-center justify-center">
                <div className="flex-grow border-t border-gray-300"></div>
                <span className="mx-4 text-gray-500">or</span>
                <div className="flex-grow border-t border-gray-300"></div>
            </div>

            <OAuthButtons className="mt-4" />
        </form>
    );
};

export default LoginForm;
