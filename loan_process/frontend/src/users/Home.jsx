import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import API from './api';

const Home = () => {
    const [userData, setUserData] = useState(null);
    const [loanCount, setLoanCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const userRes = await API.get('/api/users/me/');
                setUserData(userRes.data);
                
                // Fetch loan count
                const loanRes = await API.get('/api/loans/');
                setLoanCount(loanRes.data.length || 0);
            } catch (err) {
                console.error('Error fetching user data:', err);
                setError(
                    err.response?.status === 401
                        ? 'Unauthorized access. Please log in again.'
                        : 'Failed to load user data. Please try again later.'
                );
            } finally {
                setIsLoading(false);
            }
        };

        fetchUserData();
    }, []);

    if (isLoading) {
        return (
            <div className="flex justify-center items-center h-64">
                <p className="text-lg">Loading...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 max-w-4xl mx-auto">
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-4 max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold mb-6">Welcome to Your Dashboard</h1>
            
            {userData && (
                <div className="bg-white shadow-md rounded-lg p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">Account Overview</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <p className="text-gray-600">Username</p>
                            <p className="font-medium">{userData.username}</p>
                        </div>
                        <div>
                            <p className="text-gray-600">Email</p>
                            <p className="font-medium">{userData.email}</p>
                        </div>
                        <div>
                            <p className="text-gray-600">KYC Status</p>
                            <p className="font-medium">
                                {userData.is_kyc_verified ? (
                                    <span className="text-green-600">Verified ✓</span>
                                ) : (
                                    <span className="text-yellow-600">Not Verified</span>
                                )}
                            </p>
                        </div>
                        <div>
                            <p className="text-gray-600">Credit Score</p>
                            <p className="font-medium">{userData.credit_score || 'Not available'}</p>
                        </div>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white shadow-md rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">Loan Applications</h2>
                    <p className="mb-4">You have <span className="font-bold">{loanCount}</span> loan application(s).</p>
                    <div className="flex flex-col space-y-2">
                        <Link 
                            to="/loans" 
                            className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded text-center"
                        >
                            View My Loans
                        </Link>
                        <Link 
                            to="/loans/apply" 
                            className="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded text-center"
                        >
                            Apply for a New Loan
                        </Link>
                    </div>
                </div>

                <div className="bg-white shadow-md rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">Quick Links</h2>
                    <div className="grid grid-cols-1 gap-2">
                        <Link 
                            to="/profile" 
                            className="bg-gray-200 hover:bg-gray-300 py-2 px-4 rounded text-center"
                        >
                            My Profile
                        </Link>
                        {userData && !userData.is_kyc_verified && (
                            <Link 
                                to="/mock/kyc" 
                                className="bg-yellow-100 hover:bg-yellow-200 py-2 px-4 rounded text-center"
                            >
                                Complete KYC Verification
                            </Link>
                        )}
                        <Link 
                            to="/document/upload" 
                            className="bg-gray-200 hover:bg-gray-300 py-2 px-4 rounded text-center"
                        >
                            Upload Documents
                        </Link>
                        <Link 
                            to="/rescore" 
                            className="bg-gray-200 hover:bg-gray-300 py-2 px-4 rounded text-center"
                        >
                            Request Credit Rescore
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;