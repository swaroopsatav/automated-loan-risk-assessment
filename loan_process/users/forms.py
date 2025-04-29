from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'phone_number', 'date_of_birth', 'address',
            'annual_income', 'employment_status',
            'govt_id_type', 'govt_id_number',
            'id_proof', 'address_proof', 'income_proof',
        )
        field_order = [
            'username', 'email', 'phone_number',
            'date_of_birth', 'address',
            'annual_income', 'employment_status',
            'govt_id_type', 'govt_id_number',
            'id_proof', 'address_proof', 'income_proof',
        ]

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            phone_number = phone_number.strip()
            if not phone_number.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            if len(phone_number) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone_number

    def clean_govt_id_number(self):
        id_number = self.cleaned_data.get('govt_id_number')
        id_type = self.cleaned_data.get('govt_id_type')

        if id_number:
            id_number = id_number.strip()
            if len(id_number) < 6:
                raise forms.ValidationError("Government ID number must be at least 6 characters long.")

            if id_type == 'SSN' and (len(id_number) != 9 or not id_number.isdigit()):
                raise forms.ValidationError("Invalid SSN format")
            elif id_type == 'Passport' and len(id_number) != 9:
                raise forms.ValidationError("Invalid passport number format")

        return id_number


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'phone_number', 'date_of_birth', 'address',
            'annual_income', 'employment_status',
            'govt_id_type', 'govt_id_number',
            'id_proof', 'address_proof', 'income_proof',
            'is_kyc_verified',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.is_kyc_verified:
            self.fields['govt_id_type'].disabled = True
            self.fields['govt_id_number'].disabled = True

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            phone_number = phone_number.strip()
            if not phone_number.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            if len(phone_number) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone_number

    def clean_govt_id_number(self):
        id_number = self.cleaned_data.get('govt_id_number')
        id_type = self.cleaned_data.get('govt_id_type')

        if id_number:
            id_number = id_number.strip()
            if len(id_number) < 6:
                raise forms.ValidationError("Government ID number must be at least 6 characters long.")

            if id_type == 'SSN' and (len(id_number) != 9 or not id_number.isdigit()):
                raise forms.ValidationError("Invalid SSN format")
            elif id_type == 'Passport' and len(id_number) != 9:
                raise forms.ValidationError("Invalid passport number format")

        return id_number
