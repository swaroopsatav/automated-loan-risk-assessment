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

    // Basic client-side validation
    if (!form.amount_requested || !form.purpose || !form.term_months) {
      setMessage('Please fill out all required fields.');
      setIsSubmitting(false);
      return;
    }

    if (form.amount_requested <= 0 || form.term_months <= 0) {
      setMessage('Loan amount and term must be positive values.');
      setIsSubmitting(false);
      return;
    }

    try {
      await loanAPI.post('api/loans/submission/', form);
      setMessage('Loan submitted successfully.');
      setForm({
        amount_requested: '',
        purpose: '',
        term_months: '',
        monthly_income: '',
        existing_loans: false,
      }); // Reset form after submission
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
      {message && <p className="text-red-500">{message}</p>} {/* Show message in red if error */}

      <div>
        <input
          name="amount_requested"
          type="number"
          placeholder="Loan Amount"
          value={form.amount_requested}
          onChange={handleChange}
          required
          className="w-full p-2 border rounded"
        />
      </div>

      <div>
        <input
          name="purpose"
          type="text"
          placeholder="Purpose"
          value={form.purpose}
          onChange={handleChange}
          required
          className="w-full p-2 border rounded"
        />
      </div>

      <div>
        <input
          name="term_months"
          type="number"
          placeholder="Term (months)"
          value={form.term_months}
          onChange={handleChange}
          required
          className="w-full p-2 border rounded"
        />
      </div>

      <div>
        <input
          name="monthly_income"
          type="number"
          placeholder="Monthly Income"
          value={form.monthly_income}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        />
      </div>

      <div>
        <label>
          <input
            name="existing_loans"
            type="checkbox"
            checked={form.existing_loans}
            onChange={handleChange}
          />
          Existing Loans
        </label>
      </div>

      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded w-full"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
};

export default LoanSubmitForm;
