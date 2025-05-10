from django.contrib import admin
from django.http import HttpResponse
from django.contrib import messages
import csv
from creditscorings.models import CreditScoreRecord
from creditscorings.utils import score_and_record
from asgiref.sync import async_to_sync


@admin.action(description="Export selected to CSV")
def export_to_csv(modeladmin, request, queryset):
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="credit_scores.csv"'

        writer = csv.writer(response)
        writer.writerow(['User', 'Loan ID', 'Model Name', 'Score', 'Decision', 'Created At'])

        for obj in queryset:
            writer.writerow([
                getattr(obj.user, 'username', 'N/A'),
                getattr(obj.loan_application, 'id', 'N/A'),
                obj.model_name,
                obj.risk_score,
                obj.decision,
                obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
        return response
    except Exception as e:
        messages.error(request, f"Error exporting to CSV: {str(e)}")
        return None


@admin.action(description="Rescore selected loans with current model")
def rescore_selected(modeladmin, request, queryset):
    success_count = 0
    error_count = 0

    for record in queryset:
        try:
            loan = record.loan_application
            if loan:
                record.delete()
                async_to_sync(score_and_record)(loan)
                success_count += 1
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            messages.error(request, f"Error rescoring loan {record.id}: {str(e)}")

    if success_count:
        messages.success(request, f"Successfully rescored {success_count} loan(s)")
    if error_count:
        messages.warning(request, f"Failed to rescore {error_count} loan(s)")


@admin.register(CreditScoreRecord)
class CreditScoreRecordAdmin(admin.ModelAdmin):
    actions = [rescore_selected, export_to_csv]
    list_display = ('id', 'user', 'loan_info', 'model_name', 'risk_score', 'decision', 'created_at')
    list_filter = ('model_name', 'decision', 'created_at')
    search_fields = ('user__username', 'loan_application__id', 'model_name')
    ordering = ('-created_at',)

    readonly_fields = (
        'user', 'loan_application', 'model_name',
        'risk_score', 'decision', 'scoring_inputs', 'scoring_output', 'created_at'
    )

    fieldsets = (
        (None, {
            'fields': ('user', 'loan_application', 'model_name', 'created_at')
        }),
        ("Scoring Result", {
            'fields': ('risk_score', 'decision')
        }),
        ("Inputs & Output", {
            'fields': ('scoring_inputs', 'scoring_output')
        }),
    )

    def loan_info(self, obj):
        if obj.loan_application:
            return f"Loan #{obj.loan_application.id} — ₹{obj.loan_application.amount_requested:,} / {obj.loan_application.term_months} months"
        return "No Loan Info"

    loan_info.short_description = "Loan Info"
