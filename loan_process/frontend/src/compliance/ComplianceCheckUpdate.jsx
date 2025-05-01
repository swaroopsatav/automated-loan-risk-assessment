import React, { useEffect, useState } from 'react';
import complianceAPI from './api';
import { useParams, useNavigate } from 'react-router-dom';

const ComplianceCheckUpdate = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState({ status: '', reviewed_by: '', reviewed_at: '', notes: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCheckDetails = async () => {
      try {
        const response = await complianceAPI.get(`/api/compliance/check/${id}/`);
        setForm(response.data);
      } catch (err) {
        console.error('Error fetching check details:', err);
        setError('Failed to load compliance check details.');
      }
    };

    fetchCheckDetails();
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await complianceAPI.patch(`/api/compliance/check/${id}/`, form);
      navigate(-1); // Navigate back to the previous page
    } catch (err) {
      console.error('Error updating compliance check:', err);
      setError('Failed to update compliance check. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white shadow p-4 space-y-4 rounded">
      <h2 className="text-xl font-semibold">Update Compliance Check</h2>
      {error && <p className="text-red-500">{error}</p>}
      <select name="status" value={form.status} onChange={handleChange} required className="w-full border p-2">
        <option value="">-- Select Status --</option>
        <option value="passed">Passed</option>
        <option value="flagged">Flagged</option>
        <option value="failed">Failed</option>
      </select>
      <input
        name="reviewed_by"
        placeholder="Staff user ID"
        value={form.reviewed_by}
        onChange={handleChange}
        required
        className="w-full border p-2"
      />
      <input
        type="datetime-local"
        name="reviewed_at"
        value={form.reviewed_at}
        onChange={handleChange}
        required
        className="w-full border p-2"
      />
      <textarea
        name="notes"
        rows={3}
        placeholder="Notes"
        value={form.notes}
        onChange={handleChange}
        className="w-full border p-2"
      />
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded"
        disabled={loading}
      >
        {loading ? 'Updating...' : 'Update Check'}
      </button>
    </form>
  );
};

export default ComplianceCheckUpdate;
