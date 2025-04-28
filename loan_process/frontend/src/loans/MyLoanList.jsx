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
        const response = await loanAPI.get('loans/mine/');
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

  if (loading) return <p className="p-4 text-center">Loading...</p>;
  if (error) return <p className="p-4 text-red-500 text-center">{error}</p>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">My Loan Applications</h2>
      <ul className="space-y-2">
        {loans.map((loan) => (
          <li key={loan.id} className="p-3 bg-white shadow rounded">
            <Link to={`/loans/${loan.id}`} className="text-blue-600 font-medium">
              Loan #{loan.id} - {loan.status}
            </Link>
            <p>Amount: ₹{loan.amount_requested} | Risk: {loan.risk_score ?? 'N/A'}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MyLoanList;