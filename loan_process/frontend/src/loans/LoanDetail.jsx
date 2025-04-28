import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import loanAPI from './api';

const LoanDetail = () => {
  const { id } = useParams();
  const [loan, setLoan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLoan = async () => {
      try {
        const response = await loanAPI.get(`loans/mine/${id}/`);
        setLoan(response.data);
      } catch (err) {
        console.error('Error fetching loan details:', err);
        setError('Failed to load loan details. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchLoan();
  }, [id]);

  if (loading) return <p className="p-4 text-center">Loading...</p>;
  if (error) return <p className="p-4 text-red-500 text-center">{error}</p>;

  return (
    <div className="p-4 max-w-2xl mx-auto space-y-2 bg-white shadow rounded">
      <h2 className="text-xl font-semibold">Loan #{loan.id}</h2>
      <p><strong>Status:</strong> {loan.status}</p>
      <p><strong>Risk Score:</strong> {loan.risk_score}</p>
      <p><strong>AI Decision:</strong> {loan.ai_decision}</p>
      <p><strong>Purpose:</strong> {loan.purpose}</p>
      <p><strong>Scoring Breakdown:</strong></p>
      <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto">{JSON.stringify(loan.ml_scoring_output, null, 2)}</pre>

      <h4 className="font-medium mt-4">Documents</h4>
      <ul className="list-disc list-inside">
        {loan.documents?.map((doc) => (
          <li key={doc.id}>
            <a href={doc.file} target="_blank" rel="noopener noreferrer" className="text-blue-600">
              {doc.document_type}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LoanDetail;