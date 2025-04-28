import React, { useState } from 'react';
import loanAPI from './api';

const LoanSubmitForm = () => {
  const [form, setForm] = useState({
    amount_requested: '',
    purpose: '',
    term_months: '',
    monthly_income: '',
    existing_loans: false,
  });
  const [message, setMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage('');
    try {
      await loanAPI.post('loans/submit/', form);
      setMessage('Loan submitted successfully.');
    } catch (err) {
      console.error('Error submitting loan:', err);
      setMessage('Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto p-4 space-y-4 bg-white shadow rounded">
      <h2 className="text-xl font-bold">Apply for a Loan</h2>
      {message && <p>{message}</p>}

      <input name="amount_requested" type="number" placeholder="Loan Amount" onChange={handleChange} required />
      <input name="purpose" type="text" placeholder="Purpose" onChange={handleChange} required />
      <input name="term_months" type="number" placeholder="Term (months)" onChange={handleChange} required />
      <input name="monthly_income" type="number" placeholder="Monthly Income" onChange={handleChange} />
      <label>
        <input name="existing_loans" type="checkbox" onChange={handleChange} /> Existing Loans
      </label>

      <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};

export default LoanSubmitForm;