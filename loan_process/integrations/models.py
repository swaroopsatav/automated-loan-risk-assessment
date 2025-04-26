from django.db import models
from users.models import CustomUser
from loanapplications.models import LoanApplication
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator

class MockKYCRecord(models.Model):
    """
    Simulated response from a real-world KYC API (PAN + Aadhaar verification).
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='mock_kyc',
        help_text="The user associated with this mock KYC record."
    )
    pan_number = models.CharField(
        max_length=20,
        validators=[MinLengthValidator(10)],
        help_text="The PAN number of the user."
    )
    pan_holder_name = models.CharField(
        max_length=255,
        help_text="The name on the PAN card."
    )
    pan_verified = models.BooleanField(
        default=False,
        help_text="Indicates whether the PAN is verified."
    )
    aadhaar_last_4 = models.CharField(
        max_length=4,
        validators=[MinLengthValidator(4), MaxLengthValidator(4)],
        help_text="The last 4 digits of the Aadhaar number."
    )
    aadhaar_verified = models.BooleanField(
        default=False,
        help_text="Indicates whether the Aadhaar is verified."
    )
    dob = models.DateField(
        help_text="The date of birth of the user."
    )

    KYC_TYPE_CHOICES = [
        ('full', 'Full KYC'),
        ('simplified', 'Simplified KYC'),
    ]
    kyc_type = models.CharField(
        max_length=50,
        choices=KYC_TYPE_CHOICES,
        default='simplified',
        help_text="The type of KYC (full or simplified)."
    )

    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('failed', 'Failed'),
    ]
    verification_status = models.CharField(
        max_length=50,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        help_text="The status of the KYC verification."
    )

    VERIFICATION_SOURCE_CHOICES = [
        ('mock_provider', 'Mock Provider'),
        ('real_provider', 'Real Provider'),
    ]
    verification_source = models.CharField(
        max_length=100,
        choices=VERIFICATION_SOURCE_CHOICES,
        default='mock_provider',
        help_text="The source of the KYC verification."
    )

    mock_response = models.JSONField(
        blank=True,
        null=True,
        help_text="The raw mock response from the KYC API."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The timestamp when this record was created."
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mock KYC Record'
        verbose_name_plural = 'Mock KYC Records'

    def __str__(self):
        return f"Mock KYC: {self.user.username}"

class MockExperianReport(models.Model):
    """
    Simulated Experian-style credit report based on a real schema.
    """
    loan_application = models.ForeignKey(
        LoanApplication,
        on_delete=models.CASCADE,
        related_name='mock_experian',
        help_text="The loan application associated with this mock Experian report."
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='experian_reports',
        help_text="The user associated with this mock Experian report."
    )

    bureau_score = models.IntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(900)],
        help_text="The credit score of the user."
    )

    SCORE_BAND_CHOICES = [
        ('poor', 'Poor (300-579)'),
        ('fair', 'Fair (580-669)'),
        ('good', 'Good (670-739)'),
        ('very_good', 'Very Good (740-799)'),
        ('excellent', 'Excellent (800-900)'),  # fixed
    ]
    score_band = models.CharField(
        max_length=100,
        choices=SCORE_BAND_CHOICES,
        help_text="The band of the credit score."
    )

    REPORT_STATUS_CHOICES = [
        ('mocked', 'Mocked'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    report_status = models.CharField(
        max_length=50,
        choices=REPORT_STATUS_CHOICES,
        default='processing',
        help_text="The status of the report."
    )

    total_accounts = models.PositiveIntegerField(
        help_text="The total number of credit accounts."
    )
    active_accounts = models.PositiveIntegerField(
        help_text="The number of active credit accounts."
    )
    overdue_accounts = models.PositiveIntegerField(
        help_text="The number of overdue credit accounts."
    )
    dpd_max = models.PositiveIntegerField(
        help_text="The maximum number of Days Past Due (DPD) for credit accounts."
    )
    credit_utilization_pct = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="The percentage of credit utilization."
    )
    emi_to_income_ratio = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="The ratio of EMI to income."
    )

    tradelines = models.JSONField(
        blank=True,
        null=True,
        help_text="The tradelines in the credit report."
    )
    enquiries = models.JSONField(
        blank=True,
        null=True,
        help_text="The enquiries in the credit report."
    )
    mock_raw_report = models.JSONField(
        help_text="The raw mock API response for the credit report."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The timestamp when this report was created."
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mock Experian Report'
        verbose_name_plural = 'Mock Experian Reports'

    def __str__(self):
        return f"Experian Report (Loan #{self.loan_application.id}) for {self.user.username}"

    def clean(self):
        super().clean()
        if not self.active_accounts or not self.total_accounts or not self.overdue_accounts:
            return

        if self.active_accounts > self.total_accounts:
            raise models.ValidationError('Active accounts cannot exceed total accounts')
        if self.overdue_accounts > self.active_accounts:
            raise models.ValidationError('Overdue accounts cannot exceed active accounts')
