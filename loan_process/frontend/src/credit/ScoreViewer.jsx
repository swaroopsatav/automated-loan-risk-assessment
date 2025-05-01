import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import scoreApi from './scoreApi';

const ScoreViewer = () => {
  const { loan_id } = useParams();
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchScore = async () => {
      try {
        const response = await scoreApi.get(`/api/credit/loans/${loan_id}/score/`);
        setScore(response.data);
      } catch (err) {
        console.error('Failed to fetch score:', err);
        setError('Unable to load credit score. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchScore();
  }, [loan_id]);

  if (loading) {
    return <p className="p-4 text-center">Loading...</p>;
  }

  if (error) {
    return <p className="p-4 text-red-500 text-center">{error}</p>;
  }

  return (
    <div className="max-w-xl mx-auto bg-white shadow p-4 rounded">
      <h2 className="text-lg font-semibold mb-2">Credit Score for Loan #{score.loan_id}</h2>
      <p><strong>Risk Score:</strong> {score.risk_score}</p>
      <p><strong>Decision:</strong> {score.decision}</p>
      <p><strong>Model:</strong> {score.model_name}</p>
      <h4 className="mt-4 font-medium">Inputs</h4>
      <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto">
        {score.scoring_inputs ? JSON.stringify(score.scoring_inputs, null, 2) : 'No inputs available'}
      </pre>
      <h4 className="mt-2 font-medium">Output / Explanation</h4>
      <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto">
        {score.scoring_output ? JSON.stringify(score.scoring_output, null, 2) : 'No output available'}
      </pre>
    </div>
  );
};

export default ScoreViewer;
