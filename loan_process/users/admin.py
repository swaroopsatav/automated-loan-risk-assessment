from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from django.utils.timezone import now
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm
import logging

logger = logging.getLogger(__name__)


@admin.action(description="Mark selected users as KYC Verified")
def mark_kyc_verified(modeladmin, request, queryset):
    """
    Admin action to mark selected users as KYC Verified.
    """
    updated_count = queryset.update(
        is_kyc_verified=True,
        kyc_verified_on=now()
    )
    logger.info(f"KYC Verified updated for {updated_count} user(s).")
    if modeladmin is not None:
        modeladmin.message_user(request, f"Successfully marked {updated_count} user(s) as KYC Verified.")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    actions = [mark_kyc_verified]

    list_display = (
        'username', 'email', 'phone_number',
        'is_kyc_verified', 'credit_score',
        'experian_status', 'last_experian_sync',
        'is_staff'
    )
    list_filter = (
        'is_kyc_verified', 'experian_status',
        'is_staff', 'is_superuser', 'is_active'
    )
    search_fields = ('username', 'email', 'phone_number', 'govt_id_number', 'experian_customer_ref')

    readonly_fields = (
        'kyc_verified_on', 'experian_status',
        'last_experian_sync', 'credit_history_fetched',
        'credit_score', 'experian_customer_ref',
        'preview_id_proof', 'preview_address_proof', 'preview_income_proof'
    )

    fieldsets = (
        *UserAdmin.fieldsets,
        ("Contact Info", {
            'fields': ('phone_number', 'date_of_birth', 'address'),
            'classes': ('wide',)
        }),
        ("Financial Info", {
            'fields': ('annual_income', 'employment_status', 'credit_score', 'credit_history_fetched'),
            'classes': ('wide',)
        }),
        ("KYC Verification", {
            'fields': (
                'is_kyc_verified', 'kyc_verified_on',
                'govt_id_type', 'govt_id_number',
                'id_proof', 'preview_id_proof',
                'address_proof', 'preview_address_proof',
                'income_proof', 'preview_income_proof',
            ),
            'classes': ('wide',)
        }),
        ("Experian Integration", {
            'fields': (
                'experian_customer_ref',
                'experian_status',
                'last_experian_sync',
            ),
            'classes': ('wide',)
        }),
    )

    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        ("Contact Info", {
            'fields': ('email', 'phone_number', 'date_of_birth', 'address'),
            'classes': ('wide',)
        }),
        ("Financial Info", {
            'fields': ('annual_income', 'employment_status'),
            'classes': ('wide',)
        }),
        ("KYC Verification", {
            'fields': (
                'govt_id_type', 'govt_id_number',
                'id_proof', 'address_proof', 'income_proof',
            ),
            'classes': ('wide',)
        }),
    )

    def preview_id_proof(self, obj):
        """
        Generate a preview link for the ID proof file.
        """
        return self._preview_file(obj.id_proof, 'ID Proof')

    preview_id_proof.short_description = "View ID Proof"

    def preview_address_proof(self, obj):
        """
        Generate a preview link for the address proof file.
        """
        return self._preview_file(obj.address_proof, 'Address Proof')

    preview_address_proof.short_description = "View Address Proof"

    def preview_income_proof(self, obj):
        """
        Generate a preview link for the income proof file.
        """
        return self._preview_file(obj.income_proof, 'Income Proof')

    preview_income_proof.short_description = "View Income Proof"

    def _preview_file(self, file_field, label):
        """
        Helper method to generate a download link for uploaded files.
        """
        if not file_field:
            return format_html('<span style="color: red;">{}</span>', "Not Uploaded")

        try:
            if hasattr(file_field, 'url') and file_field.url:
                return format_html(
                    '<a href="{}" target="_blank" class="button" style="display:inline-block; padding:5px 10px; '
                    'background:#79aec8; color:white; border-radius:3px; text-decoration:none;">'
                    '<i class="fas fa-download"></i> Download {}</a>',
                    file_field.url, label
                )
        except Exception as e:
            logger.error(f"Error generating preview link for {label}: {e}")

        return format_html('<span style="color: red;">{}</span>', "Invalid File")
