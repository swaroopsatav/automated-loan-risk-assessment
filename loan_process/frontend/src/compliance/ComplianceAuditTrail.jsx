import React, { useEffect, useState } from 'react';
import complianceAPI from './api';

const ComplianceAuditTrail = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAuditTrail = async () => {
      try {
        const response = await complianceAPI.get('compliance/audit-trail/');
        setLogs(response.data);
      } catch (err) {
        console.error('Error fetching audit trail:', err);
        setError('Failed to load audit trail. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchAuditTrail();
  }, []);

  if (loading) return <p className="p-4 text-center">Loading...</p>;
  if (error) return <p className="p-4 text-red-500 text-center">{error}</p>;

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Compliance Audit Trail</h2>
      <ul className="space-y-3">
        {logs.map((log) => (
          <li key={log.id} className="bg-white p-3 shadow rounded text-sm">
            <p><strong>{log.actor}</strong> on Loan #{log.loan_id}:</p>
            <p>→ {log.action}</p>
            <p className="text-gray-500">{new Date(log.timestamp).toLocaleString()}</p>
            {log.notes && <p className="italic text-gray-600 mt-1">{log.notes}</p>}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ComplianceAuditTrail;