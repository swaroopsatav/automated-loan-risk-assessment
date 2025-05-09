import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom';
import { resetPassword } from './auth';

const ResetPassword = () => {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState('');
    const [passwordErrors, setPasswordErrors] = useState([]);
    
    const navigate = useNavigate();
    const location = useLocation();
    
    // Get token from URL query parameters
    const queryParams = new URLSearchParams(location.search);
    const token = queryParams.get('token');
    
    useEffect(() => {
        if (!token) {
            setMessage('Invalid or missing reset token. Please request a new password reset link.');
        }
    }, [token]);
    
    const validatePassword = (password) => {
        const errors = [];
        
        if (password.length < 8) {
            errors.push('Password must be at least 8 characters long');
        }
        
        if (!/[A-Z]/.test(password)) {
            errors.push('Password must contain at least one uppercase letter');
        }
        
        if (!/[a-z]/.test(password)) {
            errors.push('Password must contain at least one lowercase letter');
        }
        
        if (!/[0-9]/.test(password)) {
            errors.push('Password must contain at least one number');
        }
        
        if (!/[^A-Za-z0-9]/.test(password)) {
            errors.push('Password must contain at least one special character');
        }
        
        setPasswordErrors(errors);
        
        // Calculate password strength
        if (errors.length === 0) {
            setPasswordStrength('strong');
        } else if (errors.length <= 2) {
            setPasswordStrength('medium');
        } else {
            setPasswordStrength('weak');
        }
        
        return errors.length === 0;
    };
    
    const handlePasswordChange = (e) => {
        const newPassword = e.target.value;
        setPassword(newPassword);
        validatePassword(newPassword);
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        
        if (!token) {
            setMessage('Invalid or missing reset token. Please request a new password reset link.');
            return;
        }
        
        if (!validatePassword(password)) {
            setMessage('Please fix the password issues before submitting');
            return;
        }
        
        if (password !== confirmPassword) {
            setMessage('Passwords do not match');
            return;
        }
        
        setIsLoading(true);
        
        try {
            const response = await resetPassword(token, password);
            
            if (response.success) {
                setIsSuccess(true);
                setMessage('Your password has been reset successfully!');
                setTimeout(() => navigate('/login'), 3000);
            } else {
                setMessage(response.message);
            }
        } catch (err) {
            console.error('Password reset error:', err);
            setMessage('An unexpected error occurred. Please try again later.');
        } finally {
            setIsLoading(false);
        }
    };
    
    const getPasswordStrengthColor = () => {
        switch (passwordStrength) {
            case 'strong':
                return 'text-green-600 border-green-400 bg-green-100';
            case 'medium':
                return 'text-yellow-600 border-yellow-400 bg-yellow-100';
            case 'weak':
                return 'text-red-600 border-red-400 bg-red-100';
            default:
                return '';
        }
    };
    
    return (
        <form 
            onSubmit={handleSubmit}
            className="p-8 max-w-md mx-auto bg-white shadow-md rounded-lg border border-gray-200"
        >
            <h2 className="text-2xl font-bold mb-4 text-center text-gray-800">RESET PASSWORD</h2>
            
            {message && (
                <p className={`text-center mb-4 border p-2 rounded-lg ${
                    isSuccess ? 'text-green-600 border-green-400 bg-green-100' : 'text-red-600 border-red-400 bg-red-100'
                }`}>
                    {message}
                </p>
            )}
            
            <div className="mb-4">
                <label htmlFor="password" className="block text-gray-700 mb-2">New Password</label>
                <input
                    type="password"
                    id="password"
                    name="password"
                    value={password}
                    onChange={handlePasswordChange}
                    placeholder="Enter your new password"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                
                {password && (
                    <div className={`mt-2 p-2 border rounded-lg ${getPasswordStrengthColor()}`}>
                        <p className="font-semibold">Password Strength: {passwordStrength}</p>
                        {passwordErrors.length > 0 && (
                            <ul className="list-disc list-inside text-sm mt-1">
                                {passwordErrors.map((error, index) => (
                                    <li key={index}>{error}</li>
                                ))}
                            </ul>
                        )}
                    </div>
                )}
            </div>
            
            <div className="mb-4">
                <label htmlFor="confirmPassword" className="block text-gray-700 mb-2">Confirm Password</label>
                <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your new password"
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {password && confirmPassword && password !== confirmPassword && (
                    <p className="text-red-600 text-sm mt-1">Passwords do not match</p>
                )}
            </div>
            
            <button
                type="submit"
                disabled={isLoading || !token}
                className={`w-full px-4 py-2 rounded-lg transition duration-300 ${
                    isLoading || !token
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

export default ResetPassword;