import React, { useEffect, useState } from 'react';
import riskAPI from './api';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip);

const RiskTrendChart = () => {
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrendData = async () => {
      try {
        const response = await riskAPI.get('/api/risk/trends/');
        setTrendData(response.data);
      } catch (err) {
        console.error('Error fetching trend data:', err);
        setError('Failed to load risk trend data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTrendData();
  }, []);

  if (loading) {
    return <p className="p-4 text-center">Loading...</p>;
  }

  if (error) {
    return <p className="p-4 text-red-500 text-center">{error}</p>;
  }

  const chartData = {
    labels: trendData.map((t) => t.date),
    datasets: [
      {
        label: 'Avg Risk Score',
        data: trendData.map((t) => t.avg_score),
        borderColor: 'blue',
        fill: false,
      },
      {
        label: 'Approval Rate',
        data: trendData.map((t) => t.approval_rate),
        borderColor: 'green',
        fill: false,
      },
      {
        label: 'Rejection Rate',
        data: trendData.map((t) => t.rejection_rate),
        borderColor: 'red',
        fill: false,
      },
    ],
  };

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Risk Trend Over Time</h2>
      <Line data={chartData} />
    </div>
  );
};

export default RiskTrendChart;
