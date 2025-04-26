from time import timezone

from django.db import models
from users.models import CustomUser
from loanapplications.models import LoanApplication


class ComplianceCheck(models.Model):
    """
    Represents a compliance check performed on a loan application.
    Tracks the type of check, its status, reviewer details, and timestamps.
    """
    CHECK_TYPES = [
        ('kyc', 'KYC Verification'),
        ('aml', 'Anti-Money Laundering'),
        ('credit_policy', 'Credit Policy Compliance'),
        ('fraud', 'Fraud Detection'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('passed', 'Passed'),
        ('flagged', 'Flagged'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='initiated_checks',
        help_text="The user who initiated this compliance check.",
        default=None
    )

    loan_application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='compliance_checks',
        help_text="The loan application being checked for compliance."
    )
    check_type = models.CharField(
        max_length=50,
        choices=CHECK_TYPES,
        help_text="The type of compliance check being performed."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The status of the compliance check."
    )
    reviewer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_checks',
        help_text="The user who reviewed this compliance check."
    )
    review_notes = models.TextField(
        blank=True,
        help_text="Notes from the compliance review."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The timestamp when the compliance check was created."
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The timestamp when the compliance check was reviewed."
    )
    is_compliant = models.BooleanField(default=False,
                                       help_text="Indicates whether the compliance check passed all requirements.")
    checked_on = models.DateTimeField(
        auto_now=True,
        help_text="The timestamp when the compliance check was last updated.",
        null=True
    )
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Compliance Check'
        verbose_name_plural = 'Compliance Checks'

    def __str__(self):
        return f"{self.get_check_type_display()} for Loan #{self.loan_application.id} - {self.status}"


class ComplianceAuditTrail(models.Model):
    """
    Records any user/admin actions taken for compliance visibility (like approvals, rejections, overrides).
    """
    ACTION_TYPES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('overridden', 'Overridden'),
        ('modified', 'Modified'),
    ]

    actor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='compliance_actions',
        help_text="The user who performed the action."
    )
    loan_application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='compliance_audit_trail',
        help_text="The loan application related to this action."
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_TYPES,
        help_text="The type of action performed."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="The timestamp when the action was performed."
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or context for the action."
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Compliance Audit Trail'
        verbose_name_plural = 'Compliance Audit Trails'

    def __str__(self):
        return f"{self.actor} - {self.get_action_display()} - Loan #{self.loan_application.id}"
