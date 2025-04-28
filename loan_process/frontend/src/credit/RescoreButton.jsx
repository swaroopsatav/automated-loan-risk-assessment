// RescoreButton.jsx
import React, { useState } from 'react';
import scoreAPI from './scoreApi';

const RescoreButton = ({ loanId }) => {
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRescore = async () => {
    setLoading(true);
    setMsg(''); // Clear any previous message

    try {
      await scoreAPI.post(`admin/rescore/${loanId}/`);
      setMsg('✅ Loan re-scored successfully.');
    } catch (err) {
      console.error('Error rescoring loan:', err);
      setMsg('❌ Failed to re-score loan. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button
        onClick={handleRescore}
        className={`px-3 py-1 rounded text-white ${
          loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-yellow-500'
        }`}
        disabled={loading}
      >
        {loading ? 'Rescoring...' : 'Rescore Loan'}
      </button>
      {msg && <p className="text-sm mt-1">{msg}</p>}
    </div>
  );
};

export default RescoreButton;