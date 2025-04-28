import React, { useEffect, useState } from 'react';
import integrationsAPI from './api';
import { Link } from 'react-router-dom';

const AdminMockExperianList = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const res = await integrationsAPI.get('mock/experian/all/');
        setReports(res.data);
      } catch (err) {
        console.error('Failed to fetch reports:', err);
        setError('Failed to load reports. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  if (loading) {
    return <div className="p-4 max-w-5xl mx-auto">Loading...</div>;
  }

  if (error) {
    return <div className="p-4 max-w-5xl mx-auto text-red-500">{error}</div>;
  }

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <h2 className="text-xl font-bold mb-4">All Mock Experian Reports</h2>
      <table className="table-auto w-full text-sm">
        <thead className="bg-gray-200 text-left">
          <tr>
            <th>User</th>
            <th>Loan</th>
            <th>Score</th>
            <th>Utilization</th>
            <th>Overdue</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report) => (
            <tr key={report.id} className="border-t">
              <td>{report.user}</td>
              <td>
                <Link to={`/mock/experian/${report.loan_application}`}>
                  #{report.loan_application}
                </Link>
              </td>
              <td>{report.bureau_score}</td>
              <td>{report.credit_utilization_pct}%</td>
              <td>{report.overdue_accounts}</td>
              <td>{new Date(report.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminMockExperianList;