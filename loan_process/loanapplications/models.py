from django.db import models
from users.models import CustomUser
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .utils.encryption_utils import EncryptedFileStorage
from asgiref.sync import async_to_sync


def loan_doc_upload_path(instance, filename):
    return f'loan_documents/loan_{instance.loan.id}/{instance.document_type}/{filename}'


class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    AI_DECISION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('manual_review', 'Manual Review'),
    ]

    # Required document types for a complete application
    REQUIRED_DOCUMENT_TYPES = [
        'bank_statement',
        'salary_slip',
        'id_proof',
        'address_proof',
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='loan_applications')

    amount_requested = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        default=0.01
    )
    purpose = models.CharField(max_length=255)
    term_months = models.PositiveIntegerField(validators=[MinValueValidator(1)],default=12)

    monthly_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        default=0.01
    )
    existing_loans = models.BooleanField(default=False)

    # AI & Risk Analysis
    risk_score = models.FloatField(null=True, blank=True)
    ai_decision = models.CharField(
        max_length=20,
        choices=AI_DECISION_CHOICES,
        null=True,
        blank=True
    )
    ml_scoring_output = models.JSONField(null=True, blank=True)

    # Status & workflow  
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    credit_score_records = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(300)]
    )

    def clean(self):
        if self.amount_requested and self.amount_requested <= 0:
            raise ValidationError({"amount_requested": ["Amount requested must be greater than zero"]})
        if self.monthly_income and self.monthly_income <= 0:
            raise ValidationError({"monthly_income": ["Monthly income must be greater than zero"]})
        if self.credit_score_records and (self.credit_score_records < 300 or self.credit_score_records > 850):
            raise ValidationError({"credit_score_records": ["Credit score must be between 300 and 850"]})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        self.clean()
        super().save(*args, **kwargs)

        # Auto-trigger scoring on new loan submission
        if is_new and self.status == 'pending':
            try:
                from creditscorings.utils import score_and_record
                async_to_sync(score_and_record)(self)
                # Update status to under_review after scoring
                self.status = 'under_review'
                super().save(update_fields=['status'])
            except Exception as e:
                import logging
                logger = logging.getLogger('loanapplications.models')
                logger.error(f"Error auto-scoring loan #{self.id}: {str(e)}")
                # Don't raise the exception to avoid breaking the save process

    def completion_percentage(self):
        """
        Calculate the completion percentage of the loan application.

        The calculation is based on:
        1. Required fields being filled (50%)
        2. Required documents being uploaded (40%)
        3. Status of the application (10%)

        Returns:
            float: Percentage of completion (0-100)
        """
        percentage = 0

        # Check required fields (50%)
        required_fields = [
            self.amount_requested,
            self.purpose,
            self.term_months,
            self.monthly_income,
            self.credit_score_records
        ]

        fields_filled = sum(1 for field in required_fields if field is not None)
        percentage += (fields_filled / len(required_fields)) * 50

        # Check required documents (40%)
        uploaded_document_types = set(
            self.documents.values_list('document_type', flat=True)
        )

        documents_uploaded = sum(1 for doc_type in self.REQUIRED_DOCUMENT_TYPES 
                                if doc_type in uploaded_document_types)
        percentage += (documents_uploaded / len(self.REQUIRED_DOCUMENT_TYPES)) * 40

        # Check status (10%)
        status_weights = {
            'pending': 0.25,
            'under_review': 0.5,
            'approved': 1.0,
            'rejected': 1.0
        }

        percentage += status_weights.get(self.status, 0) * 10

        return round(percentage, 1)


class LoanDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('bank_statement', 'Bank Statement'),
        ('salary_slip', 'Salary Slip'),
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
    ]

    loan = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(
        max_length=100,
        choices=DOCUMENT_TYPE_CHOICES
    )
    file = models.FileField(
        upload_to=loan_doc_upload_path,
        storage=EncryptedFileStorage()
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('loan', 'document_type')

    def __str__(self):
        return f"{self.get_document_type_display()} for Loan #{self.loan.id}"
