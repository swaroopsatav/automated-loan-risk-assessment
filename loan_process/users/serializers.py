from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


# Full serializer for internal/admin use
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'password',
        ]
        extra_kwargs = {
            'is_superuser': {'read_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
            'last_login': {'read_only': True},
            'date_joined': {'read_only': True},
            'user_permissions': {'read_only': True},
            'groups': {'read_only': True}
        }



# Serializer for registration (public-facing)  
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm Password")
    id_proof = serializers.FileField(required=False, allow_null=True)
    address_proof = serializers.FileField(required=False, allow_null=True)
    income_proof = serializers.FileField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True)
    govt_id_number = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password2',
            'phone_number', 'date_of_birth', 'address',
            'annual_income', 'employment_status',
            'govt_id_type', 'govt_id_number',
            'id_proof', 'address_proof', 'income_proof'
        ]
        extra_kwargs = {
            'password': {'required': True},
            'username': {'required': True},
        }

    def validate(self, data):
        # Check if both passwords are provided
        if 'password' not in data or 'password2' not in data:
            raise serializers.ValidationError({"password": "Both passwords are required."})

        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        if 'phone_number' in data:
            phone_number = data['phone_number']
            if phone_number:
                phone_number = phone_number.strip()
                if not phone_number.isdigit():
                    raise serializers.ValidationError({"phone_number": "Phone number must contain only digits."})
                if len(phone_number) != 10:
                    raise serializers.ValidationError({"phone_number": "Phone number must be exactly 10 digits."})

        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')

        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


# Read-only serializer for user dashboards
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone_number', 'address',
            'is_kyc_verified', 'kyc_verified_on',
            'credit_score', 'experian_status', 'last_experian_sync'
        ]
        read_only_fields = fields


# For safer API exposure (no PII or financials)
class SecureUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'is_kyc_verified']
        read_only_fields = fields


# Serializer for user profile updates
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'phone_number', 'date_of_birth',
            'address', 'annual_income', 'employment_status',
            'govt_id_type', 'govt_id_number'
        ]
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'read_only': True},
            'govt_id_number': {'write_only': True},
            'phone_number': {'required': False},
            'date_of_birth': {'required': False},
            'address': {'required': False},
            'annual_income': {'required': False},
            'employment_status': {'required': False},
            'govt_id_type': {'required': False}
        }
