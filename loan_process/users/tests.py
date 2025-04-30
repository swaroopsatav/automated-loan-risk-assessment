from django.apps import apps
from django.test import TestCase, SimpleTestCase
from django.contrib.admin.sites import AdminSite
from django.utils.timezone import now
from unittest.mock import Mock, patch
from .admin import CustomUserAdmin, mark_kyc_verified
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.urls import reverse, resolve
from django.core.management import call_command
from io import StringIO
from datetime import timedelta
from .apps import UsersConfig
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .serializers import (
    UserRegistrationSerializer, UserDetailSerializer,
    SecureUserSerializer, UserProfileSerializer
)
from rest_framework.test import APITestCase
from .views import (
    RegisterUserView, LoginView, UserProfileView,
    AdminUserDetailView, UserListView
)


class MockRequest:
    pass


class CustomUserAdminTest(TestCase):
    def setUp(self):
        """Set up test environment"""
        self.site = AdminSite()
        self.admin = CustomUserAdmin(CustomUser, self.site)
        self.user1 = CustomUser.objects.create(username="testuser1", is_kyc_verified=False, email="testuser1@test.com")
        self.user2 = CustomUser.objects.create(username="testuser2", is_kyc_verified=False, email='testuser2@test.com')

    def test_mark_kyc_verified(self):
        """Test the mark_kyc_verified admin action"""
        queryset = CustomUser.objects.filter(username__in=["testuser1", "testuser2"])
        mark_kyc_verified(None, MockRequest(), queryset)
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertTrue(self.user1.is_kyc_verified)
        self.assertTrue(self.user2.is_kyc_verified)
        self.assertIsNotNone(self.user1.kyc_verified_on)
        self.assertIsNotNone(self.user2.kyc_verified_on)

    def test_list_display(self):
        """Test admin list display fields"""
        list_display = self.admin.get_list_display(Mock())
        self.assertIn("username", list_display)
        self.assertIn("email", list_display)
        self.assertIn("phone_number", list_display)
        self.assertIn("is_kyc_verified", list_display)
        self.assertIn("credit_score", list_display)


class UsersConfigTest(TestCase):
    def test_app_name(self):
        """Test app name configuration"""
        app_config = apps.get_app_config('users')
        self.assertEqual(app_config.name, 'users')

    def test_app_class(self):
        """Test app class configuration"""
        app_config = apps.get_app_config('users')
        self.assertIsInstance(app_config, UsersConfig)


class CustomUserCreationFormTest(TestCase):
    def test_valid_form(self):
        """Test form validation with valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'phone_number': '1234567890',
            'date_of_birth': '1990-01-01',
            'address': '123 Test Street',
            'annual_income': 50000,
            'employment_status': 'employed',
            'govt_id_type': 'Passport',
            'govt_id_number': '123456789',
            'id_proof': None,
            'address_proof': None,
            'income_proof': None,
            'password1': 'strongpassword',
            'password2': 'strongpassword'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_phone_number(self):
        """Test form validation with invalid phone number"""
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'phone_number': '12345',  # Invalid phone number
            'date_of_birth': '1990-01-01',
            'address': '123 Test Street',
            'annual_income': 50000,
            'employment_status': 'Employed',
            'govt_id_type': 'SSN',
            'govt_id_number': '123456789',
            'id_proof': None,
            'address_proof': None,
            'income_proof': None,
            'password1': 'strongpassword',
            'password2': 'strongpassword'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Phone number must be exactly 10 digits.', form.errors['phone_number'])

    def test_invalid_govt_id_number(self):
        """Test form validation with invalid government ID"""
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'phone_number': '1234567890',
            'date_of_birth': '1990-01-01',
            'address': '123 Test Street',
            'annual_income': 50000,
            'employment_status': 'employed',
            'govt_id_type': 'Passport',
            'govt_id_number': '12345',  # Invalid government ID
            'id_proof': None,
            'address_proof': None,
            'income_proof': None,
            'password1': 'strongpassword',
            'password2': 'strongpassword'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Government ID number must be at least 6 characters long.', form.errors['govt_id_number'])


class CustomUserChangeFormTest(TestCase):
    def setUp(self):
        """Set up test user"""
        self.user = CustomUser.objects.create(
            username='testuser',
            email='testuser@example.com',
            phone_number='1234567890',
            is_kyc_verified=True
        )

    def test_readonly_fields_after_kyc(self):
        """Test if fields are readonly after KYC verification"""
        form = CustomUserChangeForm(instance=self.user)
        self.assertTrue(form.fields['govt_id_type'].disabled)
        self.assertTrue(form.fields['govt_id_number'].disabled)

    def test_clean_phone_number(self):
        """Test phone number validation"""
        form_data = {
            'username': self.user.username,
            'email': self.user.email,
            'phone_number': '12345',  # Invalid phone number
        }
        form = CustomUserChangeForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('Phone number must be exactly 10 digits.', form.errors['phone_number'])


class CustomUserModelTest(TestCase):
    def setUp(self):
        """Set up test user"""
        self.user = CustomUser.objects.create(
            username="testuser",
            email="testuser@example.com",
            phone_number="1234567890",
            date_of_birth="1990-01-01",
            annual_income=50000.00,
            employment_status="employed",
            is_kyc_verified=False
        )

    def test_user_creation(self):
        """Test user creation with valid data"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(self.user.phone_number, "1234567890")
        self.assertEqual(self.user.annual_income, 50000.00)
        self.assertEqual(self.user.employment_status, "employed")
        self.assertFalse(self.user.is_kyc_verified)

    def test_kyc_verified_on_set(self):
        """Test KYC verification timestamp"""
        self.user.is_kyc_verified = True
        self.user.save()
        self.assertIsNotNone(self.user.kyc_verified_on)
        self.assertTrue(self.user.is_kyc_verified)

    def test_document_upload_path(self):
        """Test document upload path generation"""
        path = self.user.id_proof.field.upload_to(self.user, "test_document.pdf")
        self.assertTrue(path.startswith("kyc_documents/user_"))
        self.assertTrue(path.endswith(".pdf"))

    def test_string_representation(self):
        """Test string representation of user"""
        self.assertEqual(str(self.user), "testuser (testuser@example.com)")

    def test_default_experian_status(self):
        """Test default Experian status"""
        self.assertEqual(self.user.experian_status, "pending")


class UserRegistrationSerializerTest(TestCase):
    def test_valid_registration(self):
        """Test user registration with valid data"""
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'strongpassword123',
            'password2': 'strongpassword123',
            'phone_number': '1234567890',
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_passwords_do_not_match(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'strongpassword123',
            'password2': 'differentpassword',
            'phone_number': '1234567890',
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Passwords do not match.", serializer.errors['password'])

    def test_missing_fields(self):
        """Test registration with missing required fields"""
        data = {
            'username': '',
            'email': '',
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('username', serializer.errors)

    def test_create_user(self):
        """Test user creation through serializer"""
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'strongpassword123',
            'password2': 'strongpassword123',
        }
        serializer = UserRegistrationSerializer(data=data)
        serializer.is_valid()
        user = serializer.save()
        self.assertTrue(user.check_password('strongpassword123'))
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')


class UserDetailSerializerTest(TestCase):
    def setUp(self):
        """Set up test user"""
        self.user = CustomUser.objects.create(
            username='testuser',
            email='testuser@example.com',
            phone_number='1234567890',
        )

    def test_read_only_fields(self):
        """Test read-only fields in serializer"""
        serializer = UserDetailSerializer(instance=self.user)
        data = serializer.data
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['phone_number'], self.user.phone_number)


class SecureUserSerializerTest(TestCase):
    def setUp(self):
        """Set up test user"""
        self.user = CustomUser.objects.create(
            username='testuser',
            email='testuser@example.com',
            is_kyc_verified=True,
        )

    def test_secure_user_data(self):
        """Test secure user data serialization"""
        serializer = SecureUserSerializer(instance=self.user)
        data = serializer.data
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertTrue(data['is_kyc_verified'])


class UserProfileSerializerTest(TestCase):
    def setUp(self):
        """Set up test user"""
        self.user = CustomUser.objects.create(
            username='testuser',
            email='testuser@example.com',
            phone_number='1234567890',
        )

    def test_update_profile(self):
        """Test profile update through serializer"""
        data = {
            'phone_number': '0987654321',
            'address': '123 New Street',
        }
        serializer = UserProfileSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        self.assertEqual(updated_user.phone_number, '0987654321')
        self.assertEqual(updated_user.address, '123 New Street')


class UsersUrlsTest(SimpleTestCase):
    def test_register_url_resolves(self):
        """Test register URL resolution"""
        url = reverse('users:register')
        self.assertEqual(resolve(url).func.view_class, RegisterUserView)

    def test_login_url_resolves(self):
        """Test login URL resolution"""
        url = reverse('users:login')
        self.assertEqual(resolve(url).func.view_class, LoginView)

    def test_profile_url_resolves(self):
        """Test profile URL resolution"""
        url = reverse('users:profile')
        self.assertEqual(resolve(url).func.view_class, UserProfileView)

    def test_admin_user_detail_url_resolves(self):
        """Test admin user detail URL resolution"""
        url = reverse('users:user-detail', args=[1])
        self.assertEqual(resolve(url).func.view_class, AdminUserDetailView)

    def test_admin_user_list_url_resolves(self):
        """Test admin user list URL resolution"""
        url = reverse('users:user-list')
        self.assertEqual(resolve(url).func.view_class, UserListView)


class RegisterUserViewTest(APITestCase):
    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "password2": "strongpassword123",
            "phone_number": "1234567890",
        }
        response = self.client.post(reverse("users:register"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "User registered successfully.")

    def test_register_user_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "password2": "differentpassword",
        }
        response = self.client.post(reverse("users:register"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class LoginViewTest(APITestCase):
    def setUp(self):
        """Set up test user"""
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )

    def test_login_success(self):
        """Test successful login"""
        data = {"username": "testuser", "password": "password123"}
        response = self.client.post(reverse("users:login"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(reverse("users:login"), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)


class UserProfileViewTest(APITestCase):
    def setUp(self):
        """Set up test user and authentication"""
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_get_user_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)

    def test_update_user_profile(self):
        """Test updating user profile"""
        data = {"phone_number": "0987654321", "address": "456 New Street"}
        response = self.client.put(reverse("users:profile"), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "0987654321")
        self.assertEqual(self.user.address, "456 New Street")


class AdminUserDetailViewTest(APITestCase):
    def setUp(self):
        """Set up admin user, test user, and authentication"""
        self.admin = CustomUser.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="password123"
        )
        self.token = str(RefreshToken.for_user(self.admin).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_get_user_detail(self):
        """Test retrieving user details"""
        response = self.client.get(reverse("users:user-detail", args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user.username)

    def test_user_not_found(self):
        """Test retrieving non-existent user"""
        response = self.client.get(reverse("users:user-detail", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserListViewTest(APITestCase):
    def setUp(self):
        """Set up admin user, test users, and authentication"""
        self.admin = CustomUser.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )
        self.user1 = CustomUser.objects.create_user(
            username="testuser1", email="user1@example.com", password="password123"
        )
        self.user2 = CustomUser.objects.create_user(
            username="testuser2", email="user2@example.com", password="password123"
        )
        self.token = str(RefreshToken.for_user(self.admin).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_list_users(self):
        """Test retrieving list of users"""
        response = self.client.get(reverse("users:user-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_search_users(self):
        """Test searching users"""
        response = self.client.get(reverse("users:user-list") + "?search=testuser1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["username"], "testuser1")


class CleanupInactiveUsersCommandTest(TestCase):
    def setUp(self):
        """Create active and inactive users for testing"""
        self.active_user = CustomUser.objects.create_user(
            username="active_user",
            email="active@example.com",
            password="password123",
            last_login=now()
        )
        self.inactive_user = CustomUser.objects.create_user(
            username="inactive_user",
            email="inactive@example.com",
            password="password123",
            last_login=now() - timedelta(days=365)  # inactive for a year
        )
        self.super_user = CustomUser.objects.create_superuser(
            username="super_user",
            email="superuser@example.com",
            password="password123",
            last_login=now() - timedelta(days=365)  # inactive superuser
        )

    def test_deactivate_inactive_users(self):
        """Test deactivating inactive users"""
        out = StringIO()
        call_command('cleanup_inactive_users', '--months=12', stdout=out)
        self.inactive_user.refresh_from_db()
        self.assertFalse(self.inactive_user.is_active)
        self.assertTrue(self.active_user.is_active)
        self.assertTrue(self.super_user.is_active)  # superusers must not be deactivated
        self.assertIn("✅ 1 user(s) deactivated for inactivity > 12 month(s).", out.getvalue())

    def test_delete_inactive_users(self):
        """Test deleting inactive users"""
        out = StringIO()
        call_command('cleanup_inactive_users', '--months=12', '--delete', stdout=out)
        self.assertFalse(CustomUser.objects.filter(username="inactive_user").exists())
        self.assertTrue(CustomUser.objects.filter(username="active_user").exists())
        self.assertTrue(CustomUser.objects.filter(username="super_user").exists())
        self.assertIn("✅ 1 user(s) permanently deleted for inactivity > 12 month(s).", out.getvalue())

    def test_dry_run(self):
        """Test dry run mode"""
        out = StringIO()
        call_command('cleanup_inactive_users', '--months=12', '--dry-run', stdout=out)
        self.assertTrue(CustomUser.objects.filter(username="inactive_user").exists())
        self.assertIn("✅ 1 user(s) deactivated for inactivity > 12 month(s).", out.getvalue())

    def test_no_inactive_users(self):
        """Test when no inactive users exist"""
        self.inactive_user.last_login = now()
        self.inactive_user.save()
        out = StringIO()
        call_command('cleanup_inactive_users', '--months=12', stdout=out)
        self.assertIn("✅ No inactive users to clean up.", out.getvalue())

    def test_invalid_months_argument(self):
        """Test invalid months argument"""
        out = StringIO()
        with self.assertRaises(ValueError):
            call_command('cleanup_inactive_users', '--months=-1', stdout=out)


class GenerateMockUsersCommandTest(TestCase):
    def setUp(self):
        """Set up test environment"""
        pass

    def test_generate_mock_users(self):
        """Test generating mock users"""
        out = StringIO()
        user_count = 5
        call_command('generate_mock_users', user_count, stdout=out)
        self.assertEqual(CustomUser.objects.count(), user_count)
        self.assertIn(f"✅ {user_count}/{user_count} users created...", out.getvalue())
        self.assertIn("✅ Process completed:", out.getvalue())
        self.assertIn(f"- Successfully created: {user_count} users", out.getvalue())

    def test_generate_mock_users_with_batch_size(self):
        """Test generating mock users with batch processing"""
        out = StringIO()
        user_count = 10
        batch_size = 3
        call_command('generate_mock_users', user_count, '--batch-size', batch_size, stdout=out)
        self.assertEqual(CustomUser.objects.count(), user_count)
        self.assertIn(f"✅ {user_count}/{user_count} users created...", out.getvalue())

    def test_generate_mock_users_skip_conflicts(self):
        """Test handling username conflicts"""
        CustomUser.objects.create_user(username="existing_user", email="existing@example.com", password="password123")
        out = StringIO()
        user_count = 5
        call_command('generate_mock_users', user_count, stdout=out)
        self.assertGreaterEqual(CustomUser.objects.count(), user_count)
        self.assertIn("✅ Process completed:", out.getvalue())

    def test_generate_mock_users_exceptions_handled(self):
        """Test handling exceptions during user generation"""
        out = StringIO()

        with patch('users.models.CustomUser.objects.bulk_create') as mock_bulk_create:
            mock_bulk_create.side_effect = Exception("Simulated bulk create failure")
            call_command('generate_mock_users', 5, stdout=out)

        self.assertIn("❌ Error during batch creation", out.getvalue())
