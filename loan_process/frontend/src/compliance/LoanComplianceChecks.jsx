import React, { useEffect, useState } from 'react';
import complianceAPI from './api';
import { useParams, Link } from 'react-router-dom';

const LoanComplianceChecks = () => {
  const { loanId } = useParams();
  const [checks, setChecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchComplianceChecks = async () => {
      try {
        const response = await complianceAPI.get(`compliance/loan/${loanId}/`);
        setChecks(response.data);
      } catch (err) {
        console.error('Error fetching compliance checks:', err);
        setError('Failed to load compliance checks. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchComplianceChecks();
  }, [loanId]);

  if (loading) return <p className="p-4 text-center">Loading...</p>;
  if (error) return <p className="p-4 text-red-500 text-center">{error}</p>;

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Compliance Checks for Loan #{loanId}</h2>
      {checks.map((check) => (
        <div key={check.id} className="bg-white shadow p-4 rounded mb-3">
          <p><strong>Type:</strong> {check.check_type}</p>
          <p><strong>Status:</strong> {check.status}</p>
          <p><strong>Reviewed By:</strong> {check.reviewer || '—'}</p>
          <p><strong>Notes:</strong> {check.notes || '—'}</p>
          {check.status !== 'passed' && (
            <Link
              to={`/compliance/check/${check.id}/edit`}
              className="text-blue-600 underline text-sm mt-2 inline-block"
            >
              Update
            </Link>
          )}
        </div>
      ))}
    </div>
  );
};

export default LoanComplianceChecks;