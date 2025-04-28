// AdminScoreDetail.jsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import scoreAPI from './scoreApi';
import RescoreButton from './RescoreButton';

const AdminScoreDetail = () => {
  const { id } = useParams();
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchScoreDetail = async () => {
      try {
        const response = await scoreAPI.get(`admin/scores/${id}/`);
        setScore(response.data);
      } catch (err) {
        console.error('Failed to fetch score details:', err);
        setError('Unable to load score details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchScoreDetail();
  }, [id]);

  if (loading) {
    return <p className="p-4 text-center">Loading...</p>;
  }

  if (error) {
    return <p className="p-4 text-red-500 text-center">{error}</p>;
  }

  return (
    <div className="max-w-2xl mx-auto bg-white p-4 shadow rounded">
      <h2 className="text-lg font-semibold">Admin Score Detail</h2>
      <p><strong>User:</strong> {score.user}</p>
      <p><strong>Loan ID:</strong> {score.loan_id}</p>
      <p><strong>Model:</strong> {score.model_name}</p>
      <p><strong>Risk Score:</strong> {score.risk_score}</p>
      <p><strong>Decision:</strong> {score.decision}</p>
      <h4 className="mt-4 font-medium">Inputs</h4>
      <pre className="bg-gray-100 p-2 text-sm rounded">{JSON.stringify(score.scoring_inputs, null, 2)}</pre>
      <h4 className="mt-2 font-medium">Explanation</h4>
      <pre className="bg-gray-100 p-2 text-sm rounded overflow-x-auto">{JSON.stringify(score.scoring_output, null, 2)}</pre>
      <div className="mt-4">
        <RescoreButton loanId={score.loan_id} />
      </div>
    </div>
  );
};

export default AdminScoreDetail;