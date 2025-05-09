import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import loanAPI from './api';

const LoanDetail = () => {
  const { id } = useParams();
  const [loan, setLoan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    const fetchLoan = async () => {
      try {
        const response = await loanAPI.get(`/api/loans/${id}/`);
        const cleanLoan = {
          ...response.data,
          documents: response.data.documents || [],
          ml_scoring_output: response.data.ml_scoring_output || {},
          ai_decision: response.data.ai_decision || 'Pending Review',
          risk_score: response.data.risk_score ?? 'N/A',
        };
        setLoan(cleanLoan);
      } catch (err) {
        console.error('Error fetching loan details:', err);
        if (!err.response) {
          setError('Network error. Please check your connection.');
        } else if (err.response.status === 404) {
          setError('Loan not found.');
        } else if (err.response.status === 500) {
          setError('Server error. Please try again later.');
        } else {
          setError('Failed to load loan details. Please try again later.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchLoan();
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 border-solid border-blue-600 rounded-full"></div>
      </div>
    ); // Spinner added for loading state
  }

  if (error) {
    return <p className="p-4 text-red-500 text-center">{error}</p>;
  }

  return (
    <div className="p-4 max-w-2xl mx-auto space-y-4 bg-white shadow rounded">
      <h2 className="text-xl font-semibold">Loan #{loan?.id ?? 'N/A'}</h2>
      <p><strong>Status:</strong> {loan?.status ?? 'Unknown'}</p>
      <p><strong>Risk Score:</strong> {loan?.risk_score}</p>
      <p><strong>AI Decision:</strong> {loan?.ai_decision}</p>
      <p><strong>Purpose:</strong> {loan?.purpose ?? 'N/A'}</p>

      <div>
        <strong>Scoring Breakdown:</strong>
        <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto whitespace-pre-wrap">
          {JSON.stringify(loan?.ml_scoring_output, null, 2)}
        </pre>
      </div>

      <div>
        <h4 className="font-medium mt-4">Documents</h4>
        {loan?.documents?.length > 0 ? (
          <ul className="list-disc list-inside">
            {loan?.documents.map((doc, index) => (
              <li key={doc.id ?? index}>
                <a
                  href={doc.file ?? '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {doc.document_type ?? 'Unknown Document'}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p>No documents available for this loan.</p>
        )}
      </div>
    </div>

  );
};

export default LoanDetail;
