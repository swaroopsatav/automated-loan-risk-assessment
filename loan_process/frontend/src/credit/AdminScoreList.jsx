import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import scoreApi from './scoreApi';

const AdminScoreList = () => {
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchScores = async () => {
      try {
        const response = await scoreApi.get('/api/credit/admin/scores/');
        setScores(response.data);
      } catch (err) {
        console.error('Failed to fetch scores:', err);
        setError('Unable to load scores. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchScores();
  }, []);

  if (loading) {
    return <p className="p-4 text-center">Loading...</p>;
  }

  if (error) {
    return <p className="p-4 text-red-500 text-center">{error}</p>;
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">All Credit Scores</h2>
      {scores.length > 0 ? (
        <ul className="space-y-2">
          {scores.map((score) => (
            <li key={score.id} className="bg-white p-3 rounded shadow">
              <Link to={`/admin/scores/${score.id}`} className="font-medium text-blue-600">
                Loan #{score.loan_id} — {score.user}
              </Link>
              <p>Risk: {score.risk_score} | Decision: {score.decision}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-center text-gray-600">No scores available.</p>
      )}
    </div>
  );
};

export default AdminScoreList;
