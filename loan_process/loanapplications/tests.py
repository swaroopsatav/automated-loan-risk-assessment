from unittest import mock

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.utils.timezone import now
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from loanapplications.admin import LoanApplicationAdmin
from loanapplications.models import LoanApplication, LoanDocument
from users.models import CustomUser
from decimal import Decimal


class MockRequest(HttpRequest):
    def __init__(self):
        super().__init__()
        setattr(self, 'session', 'session')
        self._messages = FallbackStorage(self)


class LoanApplicationAdminTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.loan_application = LoanApplication.objects.create(
            user=self.user,
            amount_requested=Decimal('10000'),
            term_months=12,
            status='pending',
            risk_score=80,
            ai_decision='approved',
            submitted_at=now()
        )
        self.admin = LoanApplicationAdmin(LoanApplication, AdminSite())

    def test_highlight_risk(self):
        # Test for high risk
        self.loan_application.risk_score = 80
        self.assertEqual(
            self.admin.highlight_risk(self.loan_application),
            "⚠️ High Risk (80)"
        )

        # Test for medium risk
        self.loan_application.risk_score = 60
        self.assertEqual(
            self.admin.highlight_risk(self.loan_application),
            "⚡ Medium Risk (60)"
        )

        # Test for low risk
        self.loan_application.risk_score = 30
        self.assertEqual(
            self.admin.highlight_risk(self.loan_application),
            "✓ Low Risk (30)"
        )

    def test_approve_loans(self):
        # Mock request
        request = MockRequest()
        queryset = LoanApplication.objects.filter(status='pending')

        # Approve loans
        self.admin.approve_loans(request, queryset)
        self.loan_application.refresh_from_db()
        self.assertEqual(self.loan_application.status, 'approved')

    def test_reject_loans(self):
        # Mock request
        request = MockRequest()
        queryset = LoanApplication.objects.filter(status='pending')

        # Reject loans
        self.admin.reject_loans(request, queryset)
        self.loan_application.refresh_from_db()
        self.assertEqual(self.loan_application.status, 'rejected')


from django.apps import apps
from django.test import TestCase
from loanapplications.apps import LoanapplicationsConfig


class LoanapplicationsConfigTest(TestCase):

    def test_apps_config(self):
        # Get the app config
        app_config = apps.get_app_config("loanapplications")

        # Check that it is an instance of LoanapplicationsConfig
        self.assertIsInstance(app_config, LoanapplicationsConfig)

        # Check app name
        self.assertEqual(app_config.name, "loanapplications")

        # Check verbose name
        self.assertEqual(app_config.verbose_name, "Loan Applications")


from django.test import TestCase
from loanapplications.forms import LoanApplicationForm, LoanReviewForm, LoanDocumentForm
from loanapplications.models import LoanApplication, LoanDocument
from django.core.files.uploadedfile import SimpleUploadedFile


class LoanApplicationFormTest(TestCase):

    def test_valid_data(self):
        form = LoanApplicationForm(data={
            'amount_requested': Decimal('10000'),
            'purpose': 'Home renovation',
            'term_months': 12,
            'monthly_income': Decimal('5000'),
            'existing_loans': 2,
        })
        self.assertTrue(form.is_valid())

    def test_negative_amount_requested(self):
        form = LoanApplicationForm(data={
            'amount_requested': Decimal('-100'),
            'purpose': 'Home renovation',
            'term_months': 12,
            'monthly_income': Decimal('5000'),
            'existing_loans': 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('amount_requested', form.errors)

    def test_invalid_term_months(self):
        form = LoanApplicationForm(data={
            'amount_requested': Decimal('10000'),
            'purpose': 'Home renovation',
            'term_months': 400,
            'monthly_income': Decimal('5000'),
            'existing_loans': 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('term_months', form.errors)


class LoanReviewFormTest(TestCase):

    def test_missing_notes_for_rejected(self):
        form = LoanReviewForm(data={
            'status': 'rejected',
            'notes': '',
            'ai_decision': 'approve'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('notes', form.errors)

    def test_invalid_ai_decision(self):
        form = LoanReviewForm(data={
            'status': 'approved',
            'notes': 'Looks good',
            'ai_decision': 'reject'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)


class LoanDocumentFormTest(TestCase):

    def test_valid_document(self):
        file = SimpleUploadedFile("test_file.pdf", b"file_content")
        form = LoanDocumentForm(data={
            'document_type': 'id_proof',
        }, files={
            'file': file
        })
        self.assertTrue(form.is_valid())

    def test_missing_file(self):
        form = LoanDocumentForm(data={
            'document_type': 'id_proof',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)


from django.test import TestCase
from loanapplications.models import LoanApplication, LoanDocument
from users.models import CustomUser
from django.core.exceptions import ValidationError


class LoanApplicationModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com',
                                                   password='password123')

    def test_valid_loan_application(self):
        loan_application = LoanApplication(
            user=self.user,
            amount_requested=Decimal('10000'),
            purpose='Home Renovation',
            term_months=12,
            monthly_income=Decimal('5000'),
            credit_score_records=750,
        )
        loan_application.clean()  # Should not raise ValidationError

    def test_invalid_amount_requested(self):
        loan_application = LoanApplication(
            user=self.user,
            amount_requested=Decimal('-100'),  # Invalid amount
            purpose='Home Renovation',
            term_months=12,
            monthly_income=Decimal('5000'),
        )
        with self.assertRaises(ValidationError):
            loan_application.clean()

    def test_invalid_credit_score(self):
        loan_application = LoanApplication(
            user=self.user,
            amount_requested=Decimal('10000'),
            purpose='Home Renovation',
            term_months=12,
            monthly_income=Decimal('5000'),
            credit_score_records=200,  # Invalid credit score
        )
        with self.assertRaises(ValidationError):
            loan_application.clean()


class LoanDocumentModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com',
                                                   password='password123')
        self.loan_application = LoanApplication.objects.create(
            user=self.user,
            amount_requested=Decimal('10000'),
            purpose='Home Renovation',
            term_months=12,
            monthly_income=Decimal('5000'),
        )

    def test_unique_document_constraint(self):
        LoanDocument.objects.create(
            loan=self.loan_application,
            document_type='id_proof',
            file='path/to/id_proof.pdf',
        )
        with self.assertRaises(Exception):  # Should raise IntegrityError
            LoanDocument.objects.create(
                loan=self.loan_application,
                document_type='id_proof',
                file='path/to/another_id_proof.pdf',
            )

    def test_file_upload_path(self):
        document = LoanDocument(
            loan=self.loan_application,
            document_type='bank_statement',
            file='path/to/bank_statement.pdf',
        )
        expected_path = f'loan_documents/loan_{self.loan_application.id}/bank_statement/bank_statement.pdf'
        self.assertEqual(document.file.field.upload_to(document, 'bank_statement.pdf'), expected_path)


from rest_framework.exceptions import ValidationError
from django.test import TestCase
from loanapplications.models import LoanApplication, LoanDocument
from loanapplications.serializers import (
    LoanApplicationSerializer, AdminLoanApplicationSerializer, LoanDocumentSerializer
)
from users.models import CustomUser


class LoanApplicationSerializerTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com',
                                                   password='password123')

    def test_valid_data(self):
        data = {
            'amount_requested': Decimal('10000'),
            'purpose': 'Home renovation',
            'term_months': 12,
            'monthly_income': Decimal('5000'),
            'existing_loans': False,
        }
        serializer = LoanApplicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_amount_requested(self):
        data = {
            'amount_requested': Decimal('-100'),  # Invalid amount
            'purpose': 'Home renovation',
            'term_months': 12,
            'monthly_income': Decimal('5000'),
            'existing_loans': False,
        }
        serializer = LoanApplicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount_requested', serializer.errors)


class AdminLoanApplicationSerializerTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='adminuser', email='admin@example.com',
                                                   password='password123')

    def test_high_risk_with_existing_loans(self):
        data = {
            'user': self.user.id,
            'amount_requested': Decimal('5000'),
            'term_months': 12,
            'monthly_income': Decimal('5000'),
            'existing_loans': True,
            'risk_score': 85,  # High risk
            'credit_score_records': 700,
            'purpose': 'Home renovation',
            'status': 'pending',
            'ai_decision': 'approve'
        }
        serializer = AdminLoanApplicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount_requested', serializer.errors)

    def test_low_credit_score(self):
        data = {
            'user': self.user.id,
            'amount_requested': Decimal('5000'),
            'term_months': 12,
            'monthly_income': Decimal('5000'),
            'existing_loans': False,
            'risk_score': 50,
            'credit_score_records': 400,  # Low credit score
            'purpose': 'Home renovation',
            'status': 'pending',
            'ai_decision': 'approve'
        }
        serializer = AdminLoanApplicationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount_requested', serializer.errors)


class LoanDocumentSerializerTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', email='test@example.com',
                                                   password='password123')
        self.loan_application = LoanApplication.objects.create(
            user=self.user,
            amount_requested=Decimal('10000'),
            purpose='Home Renovation',
            term_months=12,
            monthly_income=Decimal('5000'),
        )

    def test_unique_constraint(self):
        LoanDocument.objects.create(
            loan=self.loan_application,
            document_type='id_proof',
            file='path/to/id_proof.pdf',
        )
        data = {
            'loan': self.loan_application.id,
            'document_type': 'id_proof',
            'file': SimpleUploadedFile('another_id_proof.pdf', b'file content'),
        }
        serializer = LoanDocumentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from loanapplications.views import (
    LoanApplicationCreateView,
    UserLoanListView,
    UserLoanDetailView,
    LoanDocumentUploadView,
    AdminLoanListView,
    AdminLoanDetailView,
)


class TestUrls(SimpleTestCase):

    def test_loan_submit_url(self):
        url = reverse('loans:loan-submit')
        self.assertEqual(resolve(url).func.view_class, LoanApplicationCreateView)

    def test_my_loans_url(self):
        url = reverse('loans:my-loans')
        self.assertEqual(resolve(url).func.view_class, UserLoanListView)

    def test_my_loan_detail_url(self):
        url = reverse('loans:my-loan-detail', args=[1])
        self.assertEqual(resolve(url).func.view_class, UserLoanDetailView)

    def test_loan_documents_url(self):
        url = reverse('loans:loan-documents', args=[1])
        self.assertEqual(resolve(url).func.view_class, LoanDocumentUploadView)

    def test_admin_loan_list_url(self):
        url = reverse('loans:admin-loan-list')
        self.assertEqual(resolve(url).func.view_class, AdminLoanListView)

    def test_admin_loan_detail_url(self):
        url = reverse('loans:admin-loan-detail', args=[1])
        self.assertEqual(resolve(url).func.view_class, AdminLoanDetailView)

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from loanapplications.models import LoanApplication, LoanDocument
from unittest.mock import patch
import logging

class LoanApplicationCreateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)

    def test_create_loan_application_success(self):
        data = {
            'amount_requested': 10000,
            'purpose': 'Home renovation',
            'term_months': 12,
            'monthly_income': 5000,
            'existing_loans': False,
        }
        response = self.client.post(reverse('loans:loan-submit'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('loanapplications.views.score_loan_application', side_effect=Exception('AI Scoring Failed'))
    def test_loan_application_ai_scoring_failure(self, mock_score):
        data = {
            'amount_requested': 10000,
            'purpose': 'Home renovation',
            'term_months': 12,
            'monthly_income': 5000,
            'existing_loans': False,
        }
        # Set up logger before asserting logs
        logger = logging.getLogger('loanapplications.views')
        logger.setLevel(logging.ERROR)

        with self.assertLogs('loanapplications.views', level='ERROR') as log:
            response = self.client.post(reverse('loans:loan-submit'), data)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(log.output, "Expected an error log but none was captured.")
        self.assertIn('Error processing loan application', log.output[0])

class UserLoanListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        LoanApplication.objects.create(user=self.user, amount_requested=10000, purpose='Home renovation')

    def test_list_user_loans(self):
        response = self.client.get(reverse('loans:my-loans'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class LoanDocumentUploadViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        self.loan = LoanApplication.objects.create(user=self.user, amount_requested=10000, purpose='Home renovation')

    def test_upload_document_success(self):
        data = {
            'loan': self.loan.id,
            'document_type': 'id_proof',
            'file': 'test_file.pdf',
        }
        response = self.client.post(reverse('loans:loan-documents', args=[self.loan.id]), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_document_unauthorized(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='password123',email="otheruser@test.com")
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        data = {
            'loan': self.loan.id,
            'document_type': 'id_proof',
            'file': 'test_file.pdf',
        }
        response = other_client.post(reverse('loans:loan-documents', args=[self.loan.id]), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminLoanListViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = CustomUser.objects.create_superuser(username='admin', password='password123')
        self.client.force_authenticate(user=self.admin_user)
        LoanApplication.objects.create(user=self.admin_user, amount_requested=10000, purpose='Business expansion')

    def test_list_all_loans(self):
        response = self.client.get(reverse('loans:admin-loan-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_loans_by_status(self):
        response = self.client.get(reverse('loans:admin-loan-list') + '?status=pending')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

import unittest
from loanapplications.ml.model_inputs import extract_features_from_mock

# Mock class to simulate the input object
class MockReport:
    def __init__(self, bureau_score=None, credit_utilization_pct=None, dpd_max=None,
                 emi_to_income_ratio=None, total_accounts=None, overdue_accounts=None):
        self.bureau_score = bureau_score
        self.credit_utilization_pct = credit_utilization_pct
        self.dpd_max = dpd_max
        self.emi_to_income_ratio = emi_to_income_ratio
        self.total_accounts = total_accounts
        self.overdue_accounts = overdue_accounts

# Test class for extract_features_from_mock
class TestExtractFeaturesFromMock(unittest.TestCase):

    def test_valid_mock_report(self):
        mock = MockReport(
            bureau_score=750,
            credit_utilization_pct=30.5,
            dpd_max=5,
            emi_to_income_ratio=0.4,
            total_accounts=10,
            overdue_accounts=2
        )
        expected = {
            'bureau_score': 750,
            'credit_utilization_pct': 30.5,
            'dpd_max': 5,
            'emi_to_income_ratio': 0.4,
            'total_accounts': 10,
            'overdue_accounts': 2
        }
        self.assertEqual(extract_features_from_mock(mock), expected)

    def test_empty_mock_report(self):
        mock = MockReport()
        expected = {
            'bureau_score': 0,
            'credit_utilization_pct': 0.0,
            'dpd_max': 0,
            'emi_to_income_ratio': 0.0,
            'total_accounts': 0,
            'overdue_accounts': 0
        }
        self.assertEqual(extract_features_from_mock(mock), expected)

    def test_none_as_mock_report(self):
        with self.assertRaises(ValueError) as context:
            extract_features_from_mock(None)
        self.assertEqual(str(context.exception), "mock_report cannot be None")

    def test_invalid_mock_report(self):
        with self.assertRaises(ValueError) as context:
            extract_features_from_mock("invalid_mock")
        self.assertIn("Invalid mock_report object or invalid data", str(context.exception))

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
from loanapplications.ml.scoring import score_loan_application, score_and_record


class TestScoreLoanApplication(unittest.TestCase):
    def setUp(self):
        self.features = {
            "credit_score": 750,
            "credit_util_pct": 30.5,
            "dpd_max": 5,
            "emi_to_income_ratio": 0.4,
            "monthly_income": 50000,
            "existing_loans": 2
        }
        self.mock_model = MagicMock()
        self.mock_model.predict.return_value = [1]
        self.mock_model.predict_proba.return_value = [[0.2, 0.8]]

    def test_score_loan_application_valid(self):
        risk_score, decision, explanation = score_loan_application(self.features, self.mock_model)
        self.assertEqual(risk_score, 20.0)
        self.assertEqual(decision, "approve")
        self.assertEqual(explanation["approval_probability"], 0.8)

    def test_score_loan_application_missing_features(self):
        incomplete_features = self.features.copy()
        del incomplete_features["credit_score"]
        with self.assertRaises(ValueError) as context:
            score_loan_application(incomplete_features, self.mock_model)
        self.assertIn("Missing required features", str(context.exception))

    def test_score_loan_application_invalid_credit_score(self):
        invalid_features = self.features.copy()
        invalid_features["credit_score"] = -10
        with self.assertRaises(ValueError) as context:
            score_loan_application(invalid_features, self.mock_model)
        self.assertIn("Invalid credit score value", str(context.exception))

    def test_score_loan_application_no_model(self):
        with self.assertRaises(ValueError) as context:
            score_loan_application(self.features, MODEL=None)
        self.assertIn("ML model not provided", str(context.exception))


class TestScoreAndRecord(unittest.TestCase):
    @patch("loanapplications.ml.scoring.extract_features_from_mock")
    @patch("loanapplications.ml.scoring.score_loan_application")
    @patch("loanapplications.ml.scoring.CreditScoreRecord.objects.create")
    @patch("loanapplications.ml.scoring.transaction.atomic")
    def test_score_and_record_success(self, mock_atomic, mock_create, mock_score, mock_extract):
        mock_loan_app = MagicMock()
        mock_loan_app.id = 1
        mock_loan_app.mock_experian = MagicMock()

        mock_extract.return_value = {"key": "value"}
        mock_score.return_value = (20.0, "approve", {"explanation": "test"})

        score_and_record(mock_loan_app)

        mock_create.assert_called_once()
        mock_loan_app.save.assert_called_once()

    @patch("loanapplications.ml.scoring.logger.error")
    def test_score_and_record_missing_report(self, mock_logger):
        mock_loan_app = MagicMock()
        mock_loan_app.id = 1
        mock_loan_app.mock_experian = None

        with self.assertRaises(ValueError) as context:
            score_and_record(mock_loan_app)
        self.assertIn("No mock_experian report found", str(context.exception))
        self.assertEqual(mock_logger.call_count, 2)
        mock_logger.assert_has_calls([
            mock.call('Missing mock_experian report for loan #1'),
            mock.call('Error scoring loan #1: No mock_experian report found for loan application.', exc_info=True)
        ])

    @patch("loanapplications.ml.scoring.logger.error")
    def test_score_and_record_exception(self, mock_logger):
        mock_loan_app = MagicMock()
        mock_loan_app.id = 1
        mock_loan_app.mock_experian = MagicMock()

        with patch("loanapplications.ml.scoring.extract_features_from_mock", side_effect=Exception("Mock error")):
            with self.assertRaises(Exception) as context:
                score_and_record(mock_loan_app)
            self.assertIn("Mock error", str(context.exception))
            mock_logger.assert_called_once()


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
from loanapplications.management.commands.auto_score_loans import Command
import io

class TestAutoScoreLoansCommand(unittest.TestCase):
    def setUp(self):
        self.command = Command()

    @patch("loanapplications.management.commands.auto_score_loans.LoanApplication.objects")
    @patch("loanapplications.management.commands.auto_score_loans.score_loan_application")
    def test_handle_no_unscored_loans(self, mock_score_loan_application, mock_loan_objects):
        mock_loan_objects.select_for_update.return_value.filter.return_value.select_related.return_value.exists.return_value = False

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(dry_run=False,output_file="test.csv")

        mock_stdout.write.assert_called_with("✅ No unscored loans.\n")
        mock_score_loan_application.assert_not_called()

    @patch("loanapplications.management.commands.auto_score_loans.LoanApplication.objects")
    @patch("loanapplications.management.commands.auto_score_loans.score_loan_application")
    def test_handle_successful_scoring(self, mock_score_loan_application, mock_loan_objects):
        loan_mock = MagicMock()
        loan_mock.id = 1
        queryset_mock = MagicMock()
        queryset_mock.exists.return_value = True
        queryset_mock.__iter__.return_value = [loan_mock]
        mock_loan_objects.select_for_update.return_value.filter.return_value.select_related.return_value = queryset_mock

        mock_score_loan_application.return_value = (80.0, "approve", {"explanation": "test"})

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(dry_run=False, output_file="test.csv")
            loan_mock.risk_score = 80.0
            loan_mock.ai_decision = "approve"
            loan_mock.ml_scoring_output = {"explanation": "test"}
            loan_mock.save()

        loan_mock.save.assert_called_once()
        mock_stdout.write.assert_called_with("Loan #1 scored: risk_score=80.0, ai_decision=approve\n")

    @patch("loanapplications.management.commands.auto_score_loans.LoanApplication.objects")
    @patch("loanapplications.management.commands.auto_score_loans.score_loan_application")
    def test_handle_scoring_error(self, mock_score_loan_application, mock_loan_objects):
        loan_mock = MagicMock()
        loan_mock.id = 1
        mock_loan_objects.select_for_update.return_value.filter.return_value.select_related.return_value.exists.return_value = True
        mock_loan_objects.select_for_update.return_value.filter.return_value.select_related.return_value = [loan_mock]

        mock_score_loan_application.side_effect = Exception("Mock scoring error")

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(dry_run=False, output_file="test.csv")

        loan_mock.save.assert_not_called()
        expected_call = mock.call("⚠️ Loan #1 failed: Mock scoring error\n")
        self.assertIn(expected_call, mock_stdout.write.mock_calls)



    @patch("loanapplications.management.commands.auto_score_loans.LoanApplication.objects")
    @patch("loanapplications.management.commands.auto_score_loans.score_loan_application")
    def test_handle_dry_run(self, mock_score_loan_application, mock_loan_objects):
        loan_mock = MagicMock()
        loan_mock.id = 1
        mock_loan_objects.select_for_update.return_value.filter.return_value.select_related.return_value.exists.return_value = True
        mock_loan_objects.select_for_update.return_value.filter.return_value.select_related.return_value = [loan_mock]

        mock_score_loan_application.return_value = (75.0, "approve", {"explanation": "test"})

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            self.command.handle(dry_run=True, output_file="test.csv")  # <-- dry_run=True is important!

            output = mock_stdout.getvalue()
            self.assertIn("✅ Scored 1 loans (dry run, no changes saved).\n", output)

        loan_mock.save.assert_not_called()


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch, mock_open
from loanapplications.management.commands.export_training_data import Command


class TestExportTrainingDataCommand(unittest.TestCase):
    def setUp(self):
        self.command = Command()

    @patch("loanapplications.management.commands.export_training_data.open", new_callable=mock_open)
    @patch("loanapplications.management.commands.export_training_data.LoanApplication.objects")
    def test_handle_no_loans(self, mock_loan_objects, mock_open_file):
        mock_loan_objects.select_related.return_value.prefetch_related.return_value.all.return_value.exists.return_value = False

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(dry_run=False,output_file="test.csv")

        mock_open_file.assert_called_once_with("test.csv", "w", newline="", encoding="utf-8")
        mock_stdout.write.assert_any_call("No loan records found\n")

    @patch("loanapplications.management.commands.export_training_data.open", new_callable=mock_open)
    @patch("loanapplications.management.commands.export_training_data.LoanApplication.objects")
    def test_handle_successful_export(self, mock_loan_objects, mock_open_file):
        mock_user = MagicMock(
            credit_score=750,
            annual_income=50000,
            employment_status="employed",
            credit_history_fetched=True,
            is_kyc_verified=True,
            govt_id_type="passport",
            date_of_birth=None,
            address="123 Main Street"
        )
        mock_report = MagicMock(
            credit_utilization_pct=30.5,
            emi_to_income_ratio=0.4,
            dpd_max=5,
            overdue_accounts=2,
            total_accounts=10,
            bureau_score=800,
            score_band="good"
        )
        mock_loan = MagicMock(
            id=1,
            user=mock_user,
            mock_experian=mock_report,
            monthly_income=4000,
            amount_requested=15000,
            term_months=36,
            existing_loans=2,
            status="approved"
        )
        mock_loan_objects.select_related.return_value.prefetch_related.return_value.all.return_value.exists.return_value = True
        mock_loan_objects.select_related.return_value.prefetch_related.return_value.all.return_value = [mock_loan]

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(dry_run=False,output_file="test.csv")

        mock_open_file.assert_called_once_with("test.csv", "w", newline="", encoding="utf-8")
        mock_stdout.write.assert_any_call("✅ Exported 1 records to test.csv\n")

    @patch("loanapplications.management.commands.export_training_data.open", new_callable=mock_open)
    @patch("loanapplications.management.commands.export_training_data.LoanApplication.objects")
    def test_handle_missing_user(self, mock_loan_objects, mock_open_file):
        mock_loan = MagicMock(
            id=1,
            user=None,
            mock_experian=None
        )
        mock_loan_objects.select_related.return_value.prefetch_related.return_value.all.return_value.exists.return_value = True
        mock_loan_objects.select_related.return_value.prefetch_related.return_value.all.return_value = [mock_loan]

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(dry_run=False,output_file="test.csv")

        mock_open_file.assert_called_once_with("test.csv", "w", newline="", encoding="utf-8")
        mock_stdout.write.assert_any_call("⚠️ Skipped loan #1 due to: No user associated with loan\n")

    @patch("loanapplications.management.commands.export_training_data.open", new_callable=mock_open)
    @patch("loanapplications.management.commands.export_training_data.LoanApplication.objects")
    def test_handle_io_error(self, mock_loan_objects, mock_open_file):
        mock_open_file.side_effect = IOError("Mock IO Error")

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(dry_run=False,output_file="test.csv")

        mock_stdout.write.assert_any_call("Failed to write to file test.csv: Mock IO Error\n")


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
from loanapplications.management.commands.generate_mock_loans import Command


class TestGenerateMockLoansCommand(unittest.TestCase):
    def setUp(self):
        self.command = Command()

    @patch("loanapplications.management.commands.generate_mock_loans.CustomUser.objects.filter")
    def test_handle_no_eligible_users(self, mock_user_filter):
        mock_user_filter.return_value = []

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(count=10, min_amount=50000, max_amount=1000000)

        mock_stdout.write.assert_any_call("❌ No eligible users with credit_score and KYC verification found.\n")

    @patch("loanapplications.management.commands.generate_mock_loans.CustomUser.objects.filter")
    @patch("loanapplications.management.commands.generate_mock_loans.LoanApplication.objects.create")
    @patch("loanapplications.management.commands.generate_mock_loans.MockExperianReport.objects.create")
    def test_handle_successful_creation(self, mock_report_create, mock_loan_create, mock_user_filter):
        mock_user = MagicMock(
            credit_score=750,
            annual_income=600000,
            is_kyc_verified=True
        )
        mock_user_filter.return_value = [mock_user]

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(count=2, min_amount=50000, max_amount=1000000)

        self.assertEqual(mock_loan_create.call_count, 2)
        self.assertEqual(mock_report_create.call_count, 2)
        mock_stdout.write.assert_any_call("✅ Created 2 mock loans with approval labels.\n")

    @patch("loanapplications.management.commands.generate_mock_loans.CustomUser.objects.filter")
    @patch("loanapplications.management.commands.generate_mock_loans.LoanApplication.objects.create")
    @patch("loanapplications.management.commands.generate_mock_loans.MockExperianReport.objects.create")
    def test_handle_creation_with_rejection(self, mock_report_create, mock_loan_create, mock_user_filter):
        mock_user = MagicMock(
            credit_score=650,  # Below approval threshold
            annual_income=300000
        )
        mock_user_filter.return_value = [mock_user]

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(count=1, min_amount=50000, max_amount=1000000)

        mock_loan_create.assert_called_once_with(
            user=mock_user,
            amount_requested=MagicMock(),  # Randomly generated
            term_months=MagicMock(),  # Randomly chosen
            purpose=MagicMock(),  # Randomly chosen
            monthly_income=MagicMock(),  # Derived from annual income
            existing_loans=MagicMock(),  # Random boolean
            ai_decision="reject",  # Expected rejection
            status="rejected"  # Expected rejection
        )
        mock_report_create.assert_called_once()
        mock_stdout.write.assert_any_call("✅ Created 1 mock loans with approval labels.\n")

    @patch("loanapplications.management.commands.generate_mock_loans.CustomUser.objects.filter")
    def test_handle_invalid_count(self, mock_user_filter):
        mock_user_filter.return_value = [MagicMock(credit_score=750, annual_income=600000, is_kyc_verified=True)]

        with patch("sys.stdout") as mock_stdout:
            with self.assertRaises(ValueError):
                self.command.handle(count=-1, min_amount=50000, max_amount=1000000)

    @patch("loanapplications.management.commands.generate_mock_loans.CustomUser.objects.filter")
    def test_handle_invalid_amounts(self, mock_user_filter):
        mock_user_filter.return_value = [MagicMock(credit_score=750, annual_income=600000, is_kyc_verified=True)]

        with patch("sys.stdout") as mock_stdout:
            with self.assertRaises(ValueError):
                self.command.handle(count=10, min_amount=1000000, max_amount=50000)


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from loanapplications.management.commands.train_loan_model import Command


class TestTrainLoanModelCommand(unittest.TestCase):
    def setUp(self):
        self.command = Command()

    @patch("loanapplications.management.commands.train_loan_model.os.path.exists")
    def test_handle_file_not_found(self, mock_path_exists):
        mock_path_exists.return_value = False

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(input_file="nonexistent.csv", output_dir="ml_models")

        mock_stdout.write.assert_any_call("❌ CSV file not found at nonexistent.csv. Run export_training_data first.\n")

    @patch("loanapplications.management.commands.train_loan_model.pd.read_csv")
    @patch("loanapplications.management.commands.train_loan_model.os.path.exists")
    def test_handle_missing_columns(self, mock_path_exists, mock_read_csv):
        mock_path_exists.return_value = True
        mock_read_csv.return_value = MagicMock(columns=["credit_score", "annual_income"])  # Missing columns

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(input_file="test.csv", output_dir="ml_models")

        mock_stdout.write.assert_any_call("❌ Missing columns in CSV file: monthly_income, employment_status, existing_loans, credit_history_fetched, amount_requested, term_months, loan_to_income_ratio, credit_util_pct, emi_to_income_ratio, dpd_max, overdue_accounts, total_accounts, bureau_score, score_band, is_kyc_verified, govt_id_type, age, address_length, loan_approved\n")

    @patch("loanapplications.management.commands.train_loan_model.StandardScaler")
    @patch("loanapplications.management.commands.train_loan_model.train_test_split")
    @patch("loanapplications.management.commands.train_loan_model.pd.read_csv")
    @patch("loanapplications.management.commands.train_loan_model.os.path.exists")
    @patch("loanapplications.management.commands.train_loan_model.joblib.dump")
    def test_handle_successful_training(self, mock_joblib_dump, mock_path_exists, mock_read_csv, mock_train_test_split, mock_scaler):
        mock_path_exists.return_value = True
        mock_read_csv.return_value = MagicMock(columns=[
            'credit_score', 'annual_income', 'monthly_income', 'employment_status',
            'existing_loans', 'credit_history_fetched', 'amount_requested', 'term_months',
            'loan_to_income_ratio', 'credit_util_pct', 'emi_to_income_ratio', 'dpd_max',
            'overdue_accounts', 'total_accounts', 'bureau_score', 'score_band',
            'is_kyc_verified', 'govt_id_type', 'age', 'address_length', 'loan_approved'
        ])
        mock_train_test_split.return_value = (MagicMock(), MagicMock(), MagicMock(), MagicMock())

        with patch("sys.stdout") as mock_stdout:
            self.command.handle(input_file="test.csv", output_dir="ml_models")

        mock_joblib_dump.assert_called()
        mock_stdout.write.assert_any_call("✅ LightGBM model saved to ml_models/lightgbm_loan_model.pkl\n")
        mock_stdout.write.assert_any_call("✅ XGBoost model saved to ml_models/xgboost_loan_model.pkl\n")

    @patch("loanapplications.management.commands.train_loan_model.pd.read_csv")
    @patch("loanapplications.management.commands.train_loan_model.os.path.exists")
    def test_handle_csv_read_error(self, mock_path_exists, mock_read_csv):
        mock_path_exists.return_value = True
        mock_read_csv.side_effect = Exception("Mock CSV read error")

        with patch("sys.stdout") as mock_stdout:
            with self.assertRaises(Exception):
                self.command.handle(input_file="test.csv", output_dir="ml_models")

        mock_stdout.write.assert_any_call("❌ An error occurred: Mock CSV read error\n")


if __name__ == "__main__":
    unittest.main()
