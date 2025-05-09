from django.contrib import admin
from django.utils import timezone
from .models import LoanApplication, LoanDocument
from .utils.email_utils import send_loan_status_update_email


class LoanDocumentInline(admin.TabularInline):
    model = LoanDocument
    extra = 0
    readonly_fields = ('uploaded_at',)
    fields = ('document_type', 'file', 'uploaded_at')


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'amount_requested', 'term_months',
        'status', 'ai_decision', 'risk_score', 'submitted_at', 'highlight_risk'
    )
    list_filter = ('status', 'ai_decision', 'existing_loans', 'submitted_at')
    search_fields = ('user__username', 'user__email', 'purpose', 'id')
    ordering = ('-submitted_at',)

    readonly_fields = (
        'submitted_at', 'reviewed_at', 'updated_at',
        'risk_score', 'ml_scoring_output',
    )

    fieldsets = (
        ("Applicant & Purpose", {
            'fields': ('user', 'amount_requested', 'term_months', 'purpose'),
        }),
        ("Financial Info", {
            'fields': ('monthly_income', 'existing_loans', 'credit_score_records'),
        }),
        ("AI Risk Scoring", {
            'fields': ('risk_score', 'ai_decision', 'ml_scoring_output'),
        }),
        ("Review & Status", {
            'fields': ('status', 'notes', 'submitted_at', 'reviewed_at', 'updated_at'),
        }),
    )

    inlines = [LoanDocumentInline]
    actions = ['approve_loans', 'reject_loans']

    def highlight_risk(self, obj):
        if not obj.risk_score:
            return "N/A"
        if obj.risk_score > 75:
            return f"⚠️ High Risk ({obj.risk_score})"
        elif obj.risk_score > 50:
            return f"⚡ Medium Risk ({obj.risk_score})"
        return f"✓ Low Risk ({obj.risk_score})"

    highlight_risk.short_description = "Risk Assessment"

    def approve_loans(self, request, queryset):
        # Get the loans that will be updated
        loans_to_update = queryset.filter(status='pending')

        # Store the IDs before updating
        loan_ids = list(loans_to_update.values_list('id', flat=True))

        # Update the loans
        updated = loans_to_update.update(
            status='approved',
            reviewed_at=timezone.now()
        )

        if updated:
            # Send email notifications
            for loan_id in loan_ids:
                try:
                    loan = LoanApplication.objects.get(id=loan_id)
                    send_loan_status_update_email(loan)
                except Exception as e:
                    self.message_user(
                        request, 
                        f"Error sending email for loan #{loan_id}: {str(e)}", 
                        level='ERROR'
                    )

            self.message_user(request, f"{updated} loan application(s) approved successfully.")
        else:
            self.message_user(request, "No eligible loans found for approval.", level='WARNING')

    approve_loans.short_description = "Approve selected loans"

    def reject_loans(self, request, queryset):
        # Get the loans that will be updated
        loans_to_update = queryset.filter(status='pending')

        # Store the IDs before updating
        loan_ids = list(loans_to_update.values_list('id', flat=True))

        # Update the loans
        updated = loans_to_update.update(
            status='rejected',
            reviewed_at=timezone.now()
        )

        if updated:
            # Send email notifications
            for loan_id in loan_ids:
                try:
                    loan = LoanApplication.objects.get(id=loan_id)
                    send_loan_status_update_email(loan)
                except Exception as e:
                    self.message_user(
                        request, 
                        f"Error sending email for loan #{loan_id}: {str(e)}", 
                        level='ERROR'
                    )

            self.message_user(request, f"{updated} loan application(s) rejected.")
        else:
            self.message_user(request, "No eligible loans found for rejection.", level='WARNING')

    reject_loans.short_description = "Reject selected loans"

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .select_related('user') \
            .prefetch_related('documents') \
            .filter(user__is_active=True)
