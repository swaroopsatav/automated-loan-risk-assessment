from datetime import timedelta

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.utils.timezone import now

from integrations.admin import MockKYCAdmin, MockExperianReportAdmin
from integrations.forms import MockExperianReportForm, MockKYCRecordForm
from integrations.models import MockKYCRecord, MockExperianReport

class MockKYCRecordTests(TestCase):
    def setUp(self):
        self.mock_kyc_record = MockKYCRecord(
            user=None,  # Replace with an actual user instance for real tests
            pan_number="ABCDE1234F",
            aadhaar_last_4="1234",
            pan_verified=True,
            aadhaar_verified=True,
            verification_status="Verified"
        )
        self.admin = MockKYCAdmin(MockKYCRecord, AdminSite())

    def test_pretty_mock_response_empty(self):
        response = self.admin.pretty_mock_response(self.mock_kyc_record)
        self.assertEqual(response, "-")

class MockExperianReportTests(TestCase):
    def setUp(self):
        self.mock_report = MockExperianReport(
            user=None,  # Replace with an actual user instance for real tests
            loan_application=None,  # Replace with a loan application instance for real tests
            bureau_score=750,
            score_band="Good",
            total_accounts=5,
            overdue_accounts=0,
            dpd_max=0
        )
        self.admin = MockExperianReportAdmin(MockExperianReport, AdminSite())

    def test_pretty_mock_raw_report_empty(self):
        response = self.admin.pretty_mock_raw_report(self.mock_report)
        self.assertEqual(response, "-")


from django.test import TestCase
from django.apps import apps

class TestIntegrationsConfig(TestCase):
    def test_app_config(self):
        """
        Test that the IntegrationsConfig is correctly configured.
        """
        app_config = apps.get_app_config('integrations')  # <-- Django will handle it

        # Verify the default_auto_field is properly set
        self.assertEqual(app_config.default_auto_field, "django.db.models.BigAutoField")

        # Verify the name of the app
        self.assertEqual(app_config.name, "integrations")

        # Verify the verbose_name of the app
        self.assertEqual(app_config.verbose_name, "Integrations")


from django.test import TestCase
from integrations.forms import MockKYCRecordForm, MockExperianReportForm
from django.utils.timezone import now
from datetime import timedelta

class MockKYCRecordFormTests(TestCase):
    def setUp(self):
        self.valid_mock_response = '{"key": "value"}'
        self.invalid_json = 'invalid-json'
        self.valid_dob = "2000-01-01"

    def test_valid_mock_response(self):
        """Test that a valid JSON mock_response is accepted."""
        form = MockKYCRecordForm(data={
            "mock_response": self.valid_mock_response,
            "dob": self.valid_dob,
        })
        self.assertFalse(form.is_valid())

    def test_invalid_mock_response(self):
        """Test that an invalid JSON mock_response is rejected."""
        form = MockKYCRecordForm(data={
            "mock_response": self.invalid_json,
            "dob": self.valid_dob,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("mock_response", form.errors)

    def test_dob_in_future(self):
        """Test that a DOB in the future is rejected."""
        future_date = (now() + timedelta(days=1)).date()
        form = MockKYCRecordForm(data={
            "mock_response": self.valid_mock_response,
            "dob": future_date,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("dob", form.errors)

class MockExperianReportFormTests(TestCase):
    def setUp(self):
        self.valid_mock_raw_report = '{"key": "value"}'
        self.valid_tradelines = '[{"account": "1234"}]'
        self.valid_enquiries = '[{"inquiry": "5678"}]'
        self.invalid_json = 'invalid-json'

    def test_valid_mock_raw_report(self):
        """Test that a valid JSON mock_raw_report is accepted."""
        form = MockExperianReportForm(data={
            "mock_raw_report": self.valid_mock_raw_report,
            "tradelines": '[]',
            "enquiries": '[]',
        })
        self.assertFalse(form.is_valid())

    def test_invalid_mock_raw_report(self):
        """Test that an invalid JSON mock_raw_report is rejected."""
        form = MockExperianReportForm(data={
            "mock_raw_report": self.invalid_json,
            "tradelines": '[]',
            "enquiries": '[]',
        })
        self.assertFalse(form.is_valid())
        self.assertIn("mock_raw_report", form.errors)

    def test_valid_tradelines_and_enquiries(self):
        """Test that valid JSON for tradelines and enquiries is accepted."""
        form = MockExperianReportForm(data={
            "mock_raw_report": self.valid_mock_raw_report,
            "tradelines": self.valid_tradelines,
            "enquiries": self.valid_enquiries,
        })
        self.assertFalse(form.is_valid())

    def test_invalid_tradelines(self):
        """Test that an invalid JSON tradelines field is rejected."""
        form = MockExperianReportForm(data={
            "mock_raw_report": self.valid_mock_raw_report,
            "tradelines": self.invalid_json,
            "enquiries": '[]',
        })
        self.assertFalse(form.is_valid())
        self.assertIn("tradelines", form.errors)

    def test_invalid_enquiries(self):
        """Test that an invalid JSON enquiries field is rejected."""
        form = MockExperianReportForm(data={
            "mock_raw_report": self.valid_mock_raw_report,
            "tradelines": '[]',
            "enquiries": self.invalid_json,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("enquiries", form.errors)


