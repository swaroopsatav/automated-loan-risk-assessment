import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from './api';
import { changePassword } from './auth';

const ProfileEditForm = () => {
    const navigate = useNavigate();
    const [profile, setProfile] = useState({
        phone_number: '',
        date_of_birth: '',
        address: '',
        annual_income: '',
        employment_status: '',
        govt_id_type: '',
        govt_id_number: ''
    });
    const [passwordData, setPasswordData] = useState({
        current_password: '',
        new_password: '',
        confirm_password: ''
    });
    const [passwordErrors, setPasswordErrors] = useState([]);
    const [passwordStrength, setPasswordStrength] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await API.get('/api/users/me/');
                // Format date to YYYY-MM-DD for input field
                const formattedProfile = {
                    ...res.data,
                    date_of_birth: res.data.date_of_birth ? new Date(res.data.date_of_birth).toISOString().split('T')[0] : ''
                };
                setProfile(formattedProfile);
            } catch (err) {
                console.error('Error fetching profile:', err);
                setError(
                    err.response?.status === 401
                        ? 'Unauthorized access. Please log in again.'
                        : 'Failed to load profile. Please try again later.'
                );
            } finally {
                setIsLoading(false);
            }
        };

        fetchProfile();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setProfile(prevProfile => ({
            ...prevProfile,
            [name]: value
        }));
    };

    const handlePasswordChange = (e) => {
        const { name, value } = e.target;
        setPasswordData(prev => ({
            ...prev,
            [name]: value
        }));

        if (name === 'new_password') {
            validatePassword(value);
        }
    };

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

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setSuccess('');

        try {
            await API.patch('/api/users/me/', profile);
            setSuccess('Profile updated successfully!');
            setTimeout(() => {
                navigate('/profile');
            }, 2000);
        } catch (err) {
            console.error('Error updating profile:', err);
            setError(
                err.response?.data?.error || 
                'Failed to update profile. Please try again later.'
            );
        } finally {
            setIsLoading(false);
        }
    };

    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        setIsChangingPassword(true);
        setError('');
        setSuccess('');

        // Validate new password
        if (!validatePassword(passwordData.new_password)) {
            setError('Please fix the password issues before submitting');
            setIsChangingPassword(false);
            return;
        }

        // Check if passwords match
        if (passwordData.new_password !== passwordData.confirm_password) {
            setError('New passwords do not match');
            setIsChangingPassword(false);
            return;
        }

        try {
            const response = await changePassword(
                passwordData.current_password,
                passwordData.new_password
            );

            if (response.success) {
                setSuccess('Password changed successfully!');
                // Clear password fields
                setPasswordData({
                    current_password: '',
                    new_password: '',
                    confirm_password: ''
                });
                setPasswordErrors([]);
                setPasswordStrength('');
            } else {
                setError(response.message);
            }
        } catch (err) {
            console.error('Error changing password:', err);
            setError('Failed to change password. Please try again later.');
        } finally {
            setIsChangingPassword(false);
        }
    };

    if (isLoading && !profile.phone_number) {
        return <p className="text-center">Loading...</p>;
    }

    return (
        <div className="p-4 max-w-xl mx-auto">
            <h2 className="text-xl font-bold mb-4">Edit Profile</h2>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            {success && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                    {success}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block font-bold mb-1">Phone Number:</label>
                    <input
                        type="text"
                        name="phone_number"
                        value={profile.phone_number || ''}
                        onChange={handleChange}
                        className="w-full border p-2 rounded"
                        placeholder="10-digit phone number"
                        maxLength="10"
                        pattern="[0-9]{10}"
                        title="Phone number must be exactly 10 digits"
                    />
                </div>

                <div>
                    <label className="block font-bold mb-1">Date of Birth:</label>
                    <input
                        type="date"
                        name="date_of_birth"
                        value={profile.date_of_birth || ''}
                        onChange={handleChange}
                        className="w-full border p-2 rounded"
                    />
                </div>

                <div>
                    <label className="block font-bold mb-1">Address:</label>
                    <textarea
                        name="address"
                        value={profile.address || ''}
                        onChange={handleChange}
                        className="w-full border p-2 rounded"
                        rows="3"
                    />
                </div>

                <div>
                    <label className="block font-bold mb-1">Annual Income:</label>
                    <input
                        type="number"
                        name="annual_income"
                        value={profile.annual_income || ''}
                        onChange={handleChange}
                        className="w-full border p-2 rounded"
                        step="0.01"
                        min="0"
                    />
                </div>

                <div>
                    <label className="block font-bold mb-1">Employment Status:</label>
                    <select
                        name="employment_status"
                        value={profile.employment_status || ''}
                        onChange={handleChange}
                        className="w-full border p-2 rounded"
                    >
                        <option value="">Select Status</option>
                        <option value="employed">Employed</option>
                        <option value="self_employed">Self Employed</option>
                        <option value="unemployed">Unemployed</option>
                        <option value="retired">Retired</option>
                    </select>
                </div>

                <div>
                    <label className="block font-bold mb-1">Government ID Type:</label>
                    <select
                        name="govt_id_type"
                        value={profile.govt_id_type || ''}
                        onChange={handleChange}
                        className="w-full border p-2 rounded"
                    >
                        <option value="">Select ID Type</option>
                        <option value="Passport">Passport</option>
                        <option value="driving_license">Driving License</option>
                        <option value="national_id">National ID</option>
                        <option value="SSN">SSN</option>
                    </select>
                </div>

                <div>
                    <label className="block font-bold mb-1">Government ID Number:</label>
                    <input
                        type="text"
                        name="govt_id_number"
                        value={profile.govt_id_number || ''}
                        onChange={handleChange}
                        className="w-full border p-2 rounded"
                        minLength="6"
                        maxLength="100"
                    />
                </div>

                <div className="flex space-x-4">
                    <button
                        type="submit"
                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                        disabled={isLoading}
                    >
                        {isLoading ? 'Saving...' : 'Save Changes'}
                    </button>

                    <button
                        type="button"
                        onClick={() => navigate('/profile')}
                        className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded"
                    >
                        Cancel
                    </button>
                </div>
            </form>

            <div className="mt-8 border-t pt-6">
                <h3 className="text-xl font-bold mb-4">Change Password</h3>

                <form onSubmit={handlePasswordSubmit} className="space-y-4">
                    <div>
                        <label className="block font-bold mb-1">Current Password:</label>
                        <input
                            type="password"
                            name="current_password"
                            value={passwordData.current_password}
                            onChange={handlePasswordChange}
                            className="w-full border p-2 rounded"
                            required
                        />
                    </div>

                    <div>
                        <label className="block font-bold mb-1">New Password:</label>
                        <input
                            type="password"
                            name="new_password"
                            value={passwordData.new_password}
                            onChange={handlePasswordChange}
                            className="w-full border p-2 rounded"
                            required
                        />

                        {passwordData.new_password && (
                            <div className={`mt-2 p-2 border rounded-lg ${
                                passwordStrength === 'strong' ? 'text-green-600 border-green-400 bg-green-100' :
                                passwordStrength === 'medium' ? 'text-yellow-600 border-yellow-400 bg-yellow-100' :
                                'text-red-600 border-red-400 bg-red-100'
                            }`}>
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

                    <div>
                        <label className="block font-bold mb-1">Confirm New Password:</label>
                        <input
                            type="password"
                            name="confirm_password"
                            value={passwordData.confirm_password}
                            onChange={handlePasswordChange}
                            className="w-full border p-2 rounded"
                            required
                        />
                        {passwordData.new_password && passwordData.confirm_password && 
                         passwordData.new_password !== passwordData.confirm_password && (
                            <p className="text-red-600 text-sm mt-1">Passwords do not match</p>
                        )}
                    </div>

                    <div>
                        <button
                            type="submit"
                            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                            disabled={isChangingPassword}
                        >
                            {isChangingPassword ? 'Changing Password...' : 'Change Password'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ProfileEditForm;
