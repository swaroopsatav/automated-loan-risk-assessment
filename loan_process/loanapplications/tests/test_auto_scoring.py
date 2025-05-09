from django.test import TestCase
from django.contrib.auth import get_user_model
from loanapplications.models import LoanApplication
from unittest.mock import patch

User = get_user_model()

class AutoScoringTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
    
    @patch('creditscorings.utils.score_and_record')
    def test_auto_scoring_on_new_loan(self, mock_score_and_record):
        """Test that scoring is automatically triggered when a new loan is created."""
        # Create a new loan application
        loan = LoanApplication.objects.create(
            user=self.user,
            amount_requested=10000,
            purpose='Test purpose',
            term_months=12,
            monthly_income=5000,
            existing_loans=False,
            credit_score_records=750
        )
        
        # Verify that score_and_record was called
        mock_score_and_record.assert_called_once_with(loan)
        
        # Verify that the loan status was updated to 'under_review'
        loan.refresh_from_db()
        self.assertEqual(loan.status, 'under_review')