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
    const data = new FormData();
    data.append('loan', loanId);
    data.append('document_type', form.document_type);
    data.append('file', form.file);
    try {
      await loanAPI.post('loans/documents/', data);
      setMessage('Uploaded successfully!');
    } catch (err) {
      console.error('Error uploading document:', err);
      setMessage('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <input type="text" name="document_type" placeholder="e.g. Bank Statement" onChange={handleChange} required />
      <input type="file" name="file" onChange={handleChange} required />
      <button type="submit" className="bg-blue-600 text-white px-3 py-1 rounded" disabled={isUploading}>
        {isUploading ? 'Uploading...' : 'Upload'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
};

export default LoanDocumentUpload;