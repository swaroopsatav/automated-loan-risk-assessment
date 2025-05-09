"""
Utility functions for sending email notifications related to ML model performance.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging
from ..models import ModelPerformanceLog

logger = logging.getLogger('riskdashboards.email')

def send_model_performance_notification(model_log, recipients=None):
    """
    Send an email notification about ML model performance.

    Args:
        model_log: The ModelPerformanceLog instance
        recipients: List of email addresses to send to (defaults to staff users)
    """
    try:
        subject = f'ML Model Performance Update: {model_log.model_version}'

        # Context for the email template
        context = {
            'model_version': model_log.model_version,
            'timestamp': model_log.timestamp,
            'accuracy': model_log.accuracy,
            'precision': model_log.precision,
            'recall': model_log.recall,
            'auc_score': model_log.auc_score,
            'f1_score': model_log.f1_score,
            'notes': model_log.notes,
            'frontend_url': settings.FRONTEND_URL,
        }

        # Render HTML content
        html_message = render_to_string('riskdashboards/emails/model_performance_update.html', context)
        plain_message = strip_tags(html_message)

        # If no recipients provided, get staff users
        if not recipients:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            staff_users = User.objects.filter(is_staff=True)
            recipients = [user.email for user in staff_users if user.email]

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent model performance notification for {model_log.model_version}")
        return True
    except Exception as e:
        logger.error(f"Failed to send model performance notification: {str(e)}")
        return False

def send_model_performance_threshold_alert(model_log, threshold_metric, threshold_value, recipients=None):
    """
    Send an alert when a model performance metric falls below a threshold.

    Args:
        model_log: The ModelPerformanceLog instance
        threshold_metric: The metric that triggered the alert (e.g., 'accuracy')
        threshold_value: The threshold value that was crossed
        recipients: List of email addresses to send to (defaults to staff users)
    """
    try:
        subject = f'ALERT: ML Model {model_log.model_version} Performance Below Threshold'

        # Get the actual value of the metric
        actual_value = getattr(model_log, threshold_metric)

        # Context for the email template
        context = {
            'model_version': model_log.model_version,
            'timestamp': model_log.timestamp,
            'threshold_metric': threshold_metric,
            'threshold_value': threshold_value,
            'actual_value': actual_value,
            'accuracy': model_log.accuracy,
            'precision': model_log.precision,
            'recall': model_log.recall,
            'auc_score': model_log.auc_score,
            'f1_score': model_log.f1_score,
            'notes': model_log.notes,
            'frontend_url': settings.FRONTEND_URL,
        }

        # Render HTML content
        html_message = render_to_string('riskdashboards/emails/model_performance_alert.html', context)
        plain_message = strip_tags(html_message)

        # If no recipients provided, get staff users
        if not recipients:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            staff_users = User.objects.filter(is_staff=True)
            recipients = [user.email for user in staff_users if user.email]

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent model performance alert for {model_log.model_version} ({threshold_metric} below {threshold_value})")
        return True
    except Exception as e:
        logger.error(f"Failed to send model performance alert: {str(e)}")
        return False