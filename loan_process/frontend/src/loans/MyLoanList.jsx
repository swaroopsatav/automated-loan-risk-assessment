import React, { useEffect, useState } from 'react';
import loanAPI from './api';
import { Link } from 'react-router-dom';

const MyLoanList = () => {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLoans = async () => {
      try {
        const response = await loanAPI.get('api/loans/');
        setLoans(response.data);
      } catch (err) {
        console.error('Error fetching loans:', err);
        setError('Failed to load loan applications. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchLoans();
  }, []);

  if (loading) {
    return (
      <div className="p-4 text-center">
        <div className="spinner-border text-blue-600" role="status">
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return <p className="p-4 text-red-500 text-center">{error}</p>;
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">My Loan Applications</h2>
      <ul className="space-y-2">
        {loans.map((loan) => (
          <li key={loan.id} className="p-3 bg-white shadow rounded">
            <Link to={`/loans/${loan.id}`} className="text-blue-600 font-medium">
              Loan #{loan.id} - <span className={`font-semibold ${loan.status === 'approved' ? 'text-green-500' : loan.status === 'rejected' ? 'text-red-500' : 'text-yellow-500'}`}>
                {loan.status}
              </span>
            </Link>
            <p>Amount: ₹{loan.amount_requested} | Risk: {loan.risk_score ?? 'N/A'}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MyLoanList;
