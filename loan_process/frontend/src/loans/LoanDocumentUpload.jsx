import React, { useState } from 'react';
import loanAPI from './api';

const LoanDocumentUpload = ({ loanId }) => {
  const [form, setForm] = useState({ document_type: '', file: null });
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setForm((prev) => ({ ...prev, [name]: files ? files[0] : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsUploading(true);
    setMessage('');

    if (!form.document_type || !form.file) {
      setMessage('Both document type and file are required.');
      setIsUploading(false);
      return;
    }

    const data = new FormData();
    data.append('loan', loanId);
    data.append('document_type', form.document_type);
    data.append('file', form.file);

    try {
      await loanAPI.post(`api/loans/${loanId}/documents/`, data);  // Fixed URL interpolation
      setMessage('Document uploaded successfully!');
    } catch (err) {
      console.error('Error uploading document:', err);
      setMessage(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <input
        type="text"
        name="document_type"
        placeholder="e.g. Bank Statement"
        onChange={handleChange}
        value={form.document_type}
        className="w-full p-2 border rounded"
        required
      />
      <input
        type="file"
        name="file"
        onChange={handleChange}
        className="w-full p-2 border rounded"
        required
      />
      <button
        type="submit"
        className="bg-blue-600 text-white px-3 py-1 rounded disabled:opacity-50"
        disabled={isUploading}
      >
        {isUploading ? 'Uploading...' : 'Upload'}
      </button>
      {message && <p className="mt-2 text-center">{message}</p>}
    </form>
  );
};

export default LoanDocumentUpload;
