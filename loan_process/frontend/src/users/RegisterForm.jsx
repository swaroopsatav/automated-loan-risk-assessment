import React, {useState} from 'react';
import API from './api.js';
import {useNavigate} from 'react-router-dom';
import OAuthButtons from './OAuthButtons';

const RegisterForm = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password2: '',
        phone_number: '',
        date_of_birth: '',
        address: '',
        annual_income: '',
        employment_status: 'employed',
        govt_id_type: 'passport',
        govt_id_number: '',
    });

    const [documents, setDocuments] = useState({
        id_proof: null,
        address_proof: null,
        income_proof: null,
    });

    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (e) => {
        const {name, value} = e.target;
        let processedValue = value;

        // Convert annual_income to number
        if (name === 'annual_income') {
            processedValue = value === '' ? '' : Number(value);
        }

        setFormData((prev) => ({...prev, [name]: processedValue}));
        if (errors[name]) {
            setErrors(prev => ({...prev, [name]: ''}));
        }
    };

    const handleFileChange = (e) => {
        const {name, files} = e.target;
        const file = files[0];

        if (file && file.size > 5 * 1024 * 1024) {
            setErrors(prev => ({...prev, [name]: 'File size must be less than 5MB'}));
            return;
        }

        const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
        if (file && !allowedTypes.includes(file.type)) {
            setErrors(prev => ({...prev, [name]: 'Only JPG, PNG and PDF files are allowed'}));
            return;
        }

        setDocuments(prev => ({...prev, [name]: file}));
        setErrors(prev => ({...prev, [name]: ''}));
    };

    const validateForm = () => {
        const newErrors = {};

        if (formData.password !== formData.password2) {
            newErrors.password2 = 'Passwords do not match';
        }

        // Enhanced password validation
        const passwordErrors = [];
        if (formData.password.length < 8) {
            passwordErrors.push('Password must be at least 8 characters');
        }
        if (!/[A-Z]/.test(formData.password)) {
            passwordErrors.push('Password must contain at least one uppercase letter');
        }
        if (!/[a-z]/.test(formData.password)) {
            passwordErrors.push('Password must contain at least one lowercase letter');
        }
        if (!/[0-9]/.test(formData.password)) {
            passwordErrors.push('Password must contain at least one number');
        }
        if (!/[^A-Za-z0-9]/.test(formData.password)) {
            passwordErrors.push('Password must contain at least one special character');
        }

        if (passwordErrors.length > 0) {
            newErrors.password = passwordErrors.join(', ');
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            newErrors.email = 'Invalid email format';
        }

        if (!formData.phone_number.match(/^\d{10}$/)) {
            newErrors.phone_number = 'Phone number must be 10 digits';
        }

        ['username', 'email', 'password', 'govt_id_number'].forEach(field => {
            if (!formData[field]) {
                newErrors[field] = 'This field is required';
            }
        });

        ['id_proof'].forEach(doc => {
            if (!documents[doc]) {
                newErrors[doc] = 'This document is required';
            }
        });

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');

        if (!validateForm()) {
            setMessage('Please fix the errors before submitting');
            return;
        }

        setIsSubmitting(true);

        const form = new FormData();
        Object.entries(formData).forEach(([key, value]) => {
            if (value !== '') form.append(key, value);
        });
        Object.entries(documents).forEach(([key, file]) => {
            if (file) form.append(key, file);
        });

        try {
            const response = await API.post('/api/users/auth/register/', form, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setMessage('Registration successful! Redirecting to login...');
            setTimeout(() => navigate('/login'), 2000);
        } catch (err) {
            console.error('Registration error:', err);
            if (err.response?.data) {
                if (typeof err.response.data === 'object') {
                    setErrors(err.response.data);
                    setMessage('Please fix the errors in the form');
                } else {
                    setMessage(err.response.data.detail || 'Registration failed. Please try again.');
                }
            } else {
                setMessage('Network error. Please try again later.');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const renderInput = (label, name, type = 'text', placeholder = '', required = false) => (
        <div>
            <label className="block text-gray-700">{label}:{required && <span className="text-red-500">*</span>}</label>
            <input
                className={`w-full border ${errors[name] ? 'border-red-500' : 'border-gray-300'} p-2 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500`}
                name={name}
                type={type}
                placeholder={placeholder}
                value={formData[name]}
                onChange={handleChange}
                required={required}
            />
            {errors[name] && <p className="text-red-500 text-xs mt-1">{errors[name]}</p>}
        </div>
    );

    return (
        <form onSubmit={handleSubmit} className="p-6 max-w-xl mx-auto bg-white shadow-md rounded-lg space-y-6">
            <h2 className="text-2xl font-bold text-gray-800 text-center">REGISTRATION</h2>
            {message && (
                <div
                    className={`${
                        message.includes('successful') ? 'text-green-500' : 'text-red-500'
                    } text-sm text-center p-2 rounded bg-gray-50`}
                    aria-live="polite"
                >
                    {message}
                </div>
            )}

            <OAuthButtons />

            <div className="my-6 flex items-center justify-center">
                <div className="flex-grow border-t border-gray-300"></div>
                <span className="mx-4 text-gray-500">or register with email</span>
                <div className="flex-grow border-t border-gray-300"></div>
            </div>

            {renderInput('Username', 'username', 'text', 'Enter username', true)}
            {renderInput('Email', 'email', 'email', 'Enter email', true)}
            {renderInput('Password', 'password', 'password', 'Enter password', true)}
            {renderInput('Confirm Password', 'password2', 'password', 'Confirm password', true)}
            {renderInput('Phone Number', 'phone_number', 'tel', '10 digit phone number')}
            {renderInput('Date of Birth', 'date_of_birth', 'date')}
            {renderInput('Address', 'address', 'text', 'Enter full address')}
            {renderInput('Annual Income', 'annual_income', 'number', 'Enter amount in USD')}

            <div>
                <label className="block text-gray-700">Employment Status:</label>
                <select
                    name="employment_status"
                    value={formData.employment_status}
                    onChange={handleChange}
                    className="w-full border border-gray-300 p-2 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                    <option value="employed">Employed</option>
                    <option value="self-employed">Self Employed</option>
                    <option value="unemployed">Unemployed</option>
                    <option value="student">Student</option>
                </select>
            </div>

            <div>
                <label className="block text-gray-700">Government ID Type:</label>
                <select
                    name="govt_id_type"
                    value={formData.govt_id_type}
                    onChange={handleChange}
                    className="w-full border border-gray-300 p-2 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                    <option value="passport">Passport</option>
                    <option value="drivers_license">Driver's License</option>
                    <option value="national_id">National ID</option>
                </select>
            </div>

            {renderInput('ID Number', 'govt_id_number', 'text', 'Enter ID number', true)}

            <div className="space-y-4">
                <div>
                    <label className="block text-gray-700">ID Proof:<span className="text-red-500">*</span></label>
                    <input
                        className={`w-full border ${errors.id_proof ? 'border-red-500' : 'border-gray-300'} p-2 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500`}
                        type="file"
                        name="id_proof"
                        onChange={handleFileChange}
                        accept=".jpg,.jpeg,.png,.pdf"
                    />
                    {errors.id_proof && <p className="text-red-500 text-xs mt-1">{errors.id_proof}</p>}
                </div>

                <div>
                    <label className="block text-gray-700">Address Proof:</label>
                    <input
                        className={`w-full border ${errors.address_proof ? 'border-red-500' : 'border-gray-300'} p-2 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500`}
                        type="file"
                        name="address_proof"
                        onChange={handleFileChange}
                        accept=".jpg,.jpeg,.png,.pdf"
                    />
                    {errors.address_proof && <p className="text-red-500 text-xs mt-1">{errors.address_proof}</p>}
                </div>

                <div>
                    <label className="block text-gray-700">Income Proof:</label>
                    <input
                        className={`w-full border ${errors.income_proof ? 'border-red-500' : 'border-gray-300'} p-2 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500`}
                        type="file"
                        name="income_proof"
                        onChange={handleFileChange}
                        accept=".jpg,.jpeg,.png,.pdf"
                    />
                    {errors.income_proof && <p className="text-red-500 text-xs mt-1">{errors.income_proof}</p>}
                </div>
            </div>

            <button
                className={`w-full bg-indigo-500 text-white py-2 px-4 rounded focus:outline-none focus:ring-2 focus:ring-indigo-400 hover:bg-indigo-600 ${
                    isSubmitting ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                type="submit"
                disabled={isSubmitting}
            >
                {isSubmitting ? 'Registering...' : 'Register'}
            </button>
        </form>
    );
};

export default RegisterForm;
