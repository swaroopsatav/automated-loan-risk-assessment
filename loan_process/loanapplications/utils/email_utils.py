"""
Utility functions for sending email notifications related to loan applications.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger('loanapplications.email')

async def send_loan_application_submitted_email(loan_application):
    """
    Send an email notification to the user when their loan application is submitted.

    Args:
        loan_application: The LoanApplication instance
    """
    try:
        subject = f'Loan Application #{loan_application.id} Received'

        # Context for the email template
        context = {
            'user': loan_application.user,
            'loan_id': loan_application.id,
            'amount': loan_application.amount_requested,
            'purpose': loan_application.purpose,
            'term_months': loan_application.term_months,
            'submitted_at': loan_application.submitted_at,
            'frontend_url': settings.FRONTEND_URL,
        }

        # Render HTML content
        html_message = render_to_string('loanapplications/emails/application_submitted.html', context)
        plain_message = strip_tags(html_message)

        # Send email asynchronously
        await sync_to_async(send_mail)(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[loan_application.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent application submitted email for loan #{loan_application.id} to {loan_application.user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send application submitted email: {str(e)}")
        return False

async def send_loan_status_update_email(loan_application):
    """
    Send an email notification to the user when their loan application status changes.

    Args:
        loan_application: The LoanApplication instance
    """
    try:
        status_display = dict(loan_application.STATUS_CHOICES).get(loan_application.status, loan_application.status)
        subject = f'Loan Application #{loan_application.id} Status Update: {status_display}'

        # Context for the email template
        context = {
            'user': loan_application.user,
            'loan_id': loan_application.id,
            'status': loan_application.status,
            'status_display': status_display,
            'amount': loan_application.amount_requested,
            'purpose': loan_application.purpose,
            'notes': loan_application.notes,
            'reviewed_at': loan_application.reviewed_at,
            'frontend_url': settings.FRONTEND_URL,
        }

        # Render HTML content
        template_name = f'loanapplications/emails/status_{loan_application.status}.html'
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)

        # Send email asynchronously
        await sync_to_async(send_mail)(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[loan_application.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent status update email for loan #{loan_application.id} to {loan_application.user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send status update email: {str(e)}")
        return False

async def send_document_uploaded_email(loan_document):
    """
    Send an email notification to the user when they upload a document for their loan application.

    Args:
        loan_document: The LoanDocument instance
    """
    try:
        loan_application = loan_document.loan
        document_type_display = dict(loan_document.DOCUMENT_TYPE_CHOICES).get(
            loan_document.document_type, loan_document.document_type
        )

        subject = f'Document Uploaded for Loan Application #{loan_application.id}'

        # Context for the email template
        context = {
            'user': loan_application.user,
            'loan_id': loan_application.id,
            'document_type': loan_document.document_type,
            'document_type_display': document_type_display,
            'uploaded_at': loan_document.uploaded_at,
            'frontend_url': settings.FRONTEND_URL,
        }

        # Render HTML content
        html_message = render_to_string('loanapplications/emails/document_uploaded.html', context)
        plain_message = strip_tags(html_message)

        # Send email asynchronously
        await sync_to_async(send_mail)(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[loan_application.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent document uploaded email for loan #{loan_application.id} to {loan_application.user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send document uploaded email: {str(e)}")
        return False
