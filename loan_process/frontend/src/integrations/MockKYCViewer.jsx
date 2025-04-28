import React, { useEffect, useState } from 'react';
import integrationsAPI from './api';

const MockKYCViewer = () => {
  const [kyc, setKyc] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchKYC = async () => {
      try {
        const response = await integrationsAPI.get('mock/kyc/');
        setKyc(response.data);
      } catch (err) {
        console.error('Failed to fetch KYC data:', err);
        setError('Failed to load KYC data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchKYC();
  }, []);

  if (loading) {
    return <div className="p-4 max-w-md mx-auto">Loading...</div>;
  }

  if (error) {
    return <div className="p-4 max-w-md mx-auto text-red-500">{error}</div>;
  }

  return (
    <div className="p-4 bg-white max-w-md mx-auto rounded shadow">
      <h2 className="text-xl font-bold mb-2">Mock KYC Record</h2>
      <p>
        <strong>PAN:</strong> {kyc.pan_number} ({kyc.pan_verified ? '✔ Verified' : '❌ Not Verified'})
      </p>
      <p>
        <strong>Aadhaar Last 4:</strong> {kyc.aadhaar_last_4} ({kyc.aadhaar_verified ? '✔ Verified' : '❌ Not Verified'})
      </p>
      <p>
        <strong>DOB:</strong> {kyc.dob}
      </p>
      <p>
        <strong>KYC Type:</strong> {kyc.kyc_type}
      </p>
      <pre className="text-sm bg-gray-100 mt-3 p-2 rounded overflow-x-auto">
        {JSON.stringify(kyc.mock_response, null, 2)}
      </pre>
    </div>
  );
};

export default MockKYCViewer;