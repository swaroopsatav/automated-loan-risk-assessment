# Email Functionality for Loan Processing System

This module provides email notification functionality for the Loan Processing System. It sends email notifications to users at various stages of the loan application process.

## Features

- Email notifications for loan application submission
- Email notifications for loan status updates (approved, rejected, under review)
- Email notifications for document uploads
- HTML email templates with responsive design

## Configuration

Email settings are configured in the Django settings file (`loan_process/settings.py`). The following settings need to be configured:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your email provider's SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your app password
DEFAULT_FROM_EMAIL = 'Loan Processing System <your-email@gmail.com>'
```

For production, you should replace the placeholder values with your actual email credentials. For Gmail, you'll need to generate an app password.

## Email Templates

Email templates are located in the `loanapplications/templates/loanapplications/emails/` directory. The following templates are available:

- `application_submitted.html`: Sent when a loan application is submitted
- `status_approved.html`: Sent when a loan application is approved
- `status_rejected.html`: Sent when a loan application is rejected
- `status_under_review.html`: Sent when a loan application is under review
- `document_uploaded.html`: Sent when a document is uploaded for a loan application

## Usage

The email functionality is integrated with the loan application workflow. Emails are automatically sent at the following points:

1. When a loan application is submitted (`LoanApplicationCreateView.create`)
2. When a loan application status changes to 'under_review' (`LoanApplicationCreateView.process_loan`)
3. When a loan application is approved or rejected (admin actions)
4. When a document is uploaded for a loan application (`LoanDocumentUploadView.perform_create`)

## Testing

A test script is provided to verify that the email functionality works correctly. To run the tests:

```bash
cd loan_process
python manage.py shell < test_email.py
```

The test script will send test emails for each type of notification. Make sure to update the recipient email address in the test script before running it.

## Troubleshooting

If emails are not being sent, check the following:

1. Verify that the email settings in `settings.py` are correct
2. Check that the SMTP server is accessible from your environment
3. For Gmail, make sure you're using an app password if you have 2-factor authentication enabled
4. Check the Django logs for any error messages related to email sending

## Development

For development, you can use Django's console email backend to view emails in the console instead of sending them:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print the emails to the console instead of sending them through an SMTP server.