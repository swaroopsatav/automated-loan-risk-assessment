"""
Tests for the email utility functions in the riskdashboards app.
"""
from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from riskdashboards.models import ModelPerformanceLog
from riskdashboards.utils.email_utils import (
    send_model_performance_notification,
    send_model_performance_threshold_alert
)

User = get_user_model()

class EmailUtilsTest(TestCase):
    """Test case for email utility functions."""

    def setUp(self):
        """Set up test data."""
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='password123'
        )
        
        # Create a model performance log
        self.model_log = ModelPerformanceLog.objects.create(
            model_version='test_model_v1',
            accuracy=0.85,
            precision=0.82,
            recall=0.78,
            auc_score=0.88,
            f1_score=0.80,
            notes='Test model performance log'
        )

    def test_send_model_performance_notification(self):
        """Test sending a model performance notification."""
        # Clear the mail outbox
        mail.outbox = []
        
        # Send the notification
        result = send_model_performance_notification(self.model_log)
        
        # Check that the email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check the email content
        email = mail.outbox[0]
        self.assertIn(f'ML Model Performance Update: {self.model_log.model_version}', email.subject)
        self.assertIn(self.model_log.model_version, email.body)
        self.assertIn('0.85', email.body)  # Check that accuracy is in the email
        
        # Check that it was sent to the staff user
        self.assertIn(self.staff_user.email, email.to)
        self.assertNotIn(self.regular_user.email, email.to)

    def test_send_model_performance_notification_with_recipients(self):
        """Test sending a model performance notification to specific recipients."""
        # Clear the mail outbox
        mail.outbox = []
        
        # Send the notification to specific recipients
        recipients = ['test1@example.com', 'test2@example.com']
        result = send_model_performance_notification(self.model_log, recipients=recipients)
        
        # Check that the email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check that it was sent to the specified recipients
        email = mail.outbox[0]
        for recipient in recipients:
            self.assertIn(recipient, email.to)
        self.assertNotIn(self.staff_user.email, email.to)

    def test_send_model_performance_threshold_alert(self):
        """Test sending a model performance threshold alert."""
        # Clear the mail outbox
        mail.outbox = []
        
        # Send the alert
        threshold_metric = 'accuracy'
        threshold_value = 0.90
        result = send_model_performance_threshold_alert(
            self.model_log, threshold_metric, threshold_value
        )
        
        # Check that the email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check the email content
        email = mail.outbox[0]
        self.assertIn(f'ALERT: ML Model {self.model_log.model_version} Performance Below Threshold', email.subject)
        self.assertIn(threshold_metric, email.body)
        self.assertIn(str(threshold_value), email.body)
        self.assertIn('0.85', email.body)  # Check that actual value is in the email
        
        # Check that it was sent to the staff user
        self.assertIn(self.staff_user.email, email.to)
        self.assertNotIn(self.regular_user.email, email.to)

    def test_send_model_performance_threshold_alert_with_recipients(self):
        """Test sending a model performance threshold alert to specific recipients."""
        # Clear the mail outbox
        mail.outbox = []
        
        # Send the alert to specific recipients
        recipients = ['alert1@example.com', 'alert2@example.com']
        threshold_metric = 'precision'
        threshold_value = 0.85
        result = send_model_performance_threshold_alert(
            self.model_log, threshold_metric, threshold_value, recipients=recipients
        )
        
        # Check that the email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Check that it was sent to the specified recipients
        email = mail.outbox[0]
        for recipient in recipients:
            self.assertIn(recipient, email.to)
        self.assertNotIn(self.staff_user.email, email.to)