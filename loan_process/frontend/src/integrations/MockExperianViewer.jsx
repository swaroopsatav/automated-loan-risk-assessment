import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import integrationsAPI from './api';

const MockExperianViewer = () => {
  const { loanId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await integrationsAPI.get(`/api/mock/experian/${loanId}/`);
        setReport(res.data);
      } catch (err) {
        console.error('Failed to fetch report:', err);
        setError('Failed to load the report. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [loanId]);

  if (loading) {
    return <div className="p-4 max-w-3xl mx-auto">Loading...</div>;
  }

  if (error) {
    return <div className="p-4 max-w-3xl mx-auto text-red-500">{error}</div>;
  }

  return (
    <div className="p-4 bg-white max-w-3xl mx-auto rounded shadow">
      <h2 className="text-xl font-bold mb-2">Mock Experian Report</h2>
      <p><strong>Bureau Score:</strong> {report.bureau_score} ({report.score_band})</p>
      <p><strong>Accounts:</strong> {report.total_accounts} total, {report.active_accounts} active</p>
      <p><strong>Overdue:</strong> {report.overdue_accounts} overdue, DPD max: {report.dpd_max} days</p>
      <p><strong>Utilization:</strong> {report.credit_utilization_pct}%</p>
      <p><strong>EMI/Income Ratio:</strong> {report.emi_to_income_ratio}</p>

      <h4 className="font-semibold mt-4">Raw Report</h4>
      <pre className="text-sm bg-gray-100 mt-2 p-2 rounded overflow-x-auto">
        {JSON.stringify(report.mock_raw_report, null, 2)}
      </pre>
    </div>
  );
};

export default MockExperianViewer;
