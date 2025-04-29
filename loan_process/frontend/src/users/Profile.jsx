import React, { useEffect, useState } from 'react';
import API from './api';

const Profile = () => {
    const [profile, setProfile] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await API.get('api/users/me/');
                setProfile(res.data);
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

    if (isLoading) {
        return <p className="text-center">Loading...</p>;
    }

    if (error) {
        return <p className="text-center text-red-600">{error}</p>;
    }

    const renderField = (label, value, type = 'text') => (
        <div>
            <label className="block font-bold">{label}:</label>
            <input
                type={type}
                value={value}
                readOnly
                aria-readonly="true"
                className="w-full border p-2 rounded"
            />
        </div>
    );

    return (
        <div className="p-4 max-w-xl mx-auto">
            <h2 className="text-xl font-bold">My Profile</h2>
            {profile ? (
                <form className="mt-4 space-y-4">
                    {renderField('Username', profile.username)}
                    {renderField('Email', profile.email, 'email')}
                    {renderField('Phone', profile.phone_number ?? 'N/A')}
                    {renderField('KYC Verified', profile.is_kyc_verified ? '✅' : '❌')}
                    {renderField('Credit Score', profile.credit_score ?? 'N/A')}
                    {renderField('Experian Sync', profile.last_experian_sync ?? 'N/A')}
                </form>
            ) : (
                <p className="text-center">
                    No profile data available. Please ensure you are logged in.
                </p>
            )}
        </div>
    );
};

export default Profile;
