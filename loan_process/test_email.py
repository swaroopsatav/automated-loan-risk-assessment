"""
Test script to verify email functionality.

Usage:
    python manage.py shell < test_email.py
"""

from django.core.mail import send_mail
from django.conf import settings
from loanapplications.models import LoanApplication, LoanDocument
from loanapplications.utils.email_utils import (
    send_loan_application_submitted_email,
    send_loan_status_update_email,
    send_document_uploaded_email,
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_email')

def test_simple_email():
    """Test sending a simple email using Django's send_mail function."""
    try:
        result = send_mail(
            subject='Test Email from Loan Processing System',
            message='This is a test email to verify that the email configuration is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['test@example.com'],  # Replace with a real email for testing
            fail_silently=False,
        )
        logger.info(f"Simple email sent: {result}")
        return result
    except Exception as e:
        logger.error(f"Error sending simple email: {str(e)}")
        return False

def test_loan_application_email():
    """Test sending a loan application submitted email."""
    try:
        # Get the first loan application
        loan = LoanApplication.objects.first()
        if not loan:
            logger.error("No loan applications found in the database.")
            return False
        
        result = send_loan_application_submitted_email(loan)
        logger.info(f"Loan application submitted email sent: {result}")
        return result
    except Exception as e:
        logger.error(f"Error sending loan application email: {str(e)}")
        return False

def test_loan_status_update_email():
    """Test sending a loan status update email."""
    try:
        # Get the first loan application
        loan = LoanApplication.objects.first()
        if not loan:
            logger.error("No loan applications found in the database.")
            return False
        
        # Test with different statuses
        for status in ['approved', 'rejected', 'under_review']:
            # Temporarily change the status for testing
            original_status = loan.status
            loan.status = status
            
            result = send_loan_status_update_email(loan)
            logger.info(f"Loan status update email ({status}) sent: {result}")
            
            # Restore original status
            loan.status = original_status
        
        return True
    except Exception as e:
        logger.error(f"Error sending loan status update email: {str(e)}")
        return False

def test_document_uploaded_email():
    """Test sending a document uploaded email."""
    try:
        # Get the first loan document
        document = LoanDocument.objects.first()
        if not document:
            logger.error("No loan documents found in the database.")
            return False
        
        result = send_document_uploaded_email(document)
        logger.info(f"Document uploaded email sent: {result}")
        return result
    except Exception as e:
        logger.error(f"Error sending document uploaded email: {str(e)}")
        return False

def run_all_tests():
    """Run all email tests."""
    logger.info("Starting email tests...")
    
    # Test simple email
    logger.info("Testing simple email...")
    test_simple_email()
    
    # Test loan application email
    logger.info("Testing loan application submitted email...")
    test_loan_application_email()
    
    # Test loan status update email
    logger.info("Testing loan status update email...")
    test_loan_status_update_email()
    
    # Test document uploaded email
    logger.info("Testing document uploaded email...")
    test_document_uploaded_email()
    
    logger.info("Email tests completed.")

if __name__ == "__main__":
    run_all_tests()