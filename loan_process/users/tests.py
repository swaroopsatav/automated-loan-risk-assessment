# from django.test import TestCase
# from django.contrib.admin.sites import AdminSite
# from django.utils.timezone import now
# from unittest.mock import Mock
# from .admin import CustomUserAdmin, mark_kyc_verified
# from .models import CustomUser
#
#
# class MockRequest:
#     pass
#
#
# class CustomUserAdminTest(TestCase):
#     def setUp(self):
#         self.site = AdminSite()
#         self.admin = CustomUserAdmin(CustomUser, self.site)
#         self.user1 = CustomUser.objects.create(username="testuser1", is_kyc_verified=False, email="testuser1@test.com")
#         self.user2 = CustomUser.objects.create(username="testuser2", is_kyc_verified=False,email='testuser2@test.com')
#
#     def test_mark_kyc_verified(self):
#         queryset = CustomUser.objects.filter(username__in=["testuser1", "testuser2"])
#         mark_kyc_verified(None, MockRequest(), queryset)
#         self.user1.refresh_from_db()
#         self.user2.refresh_from_db()
#         self.assertTrue(self.user1.is_kyc_verified)
#         self.assertTrue(self.user2.is_kyc_verified)
#         self.assertIsNotNone(self.user1.kyc_verified_on)
#         self.assertIsNotNone(self.user2.kyc_verified_on)
#
#     def test_list_display(self):
#         list_display = self.admin.get_list_display(Mock())
#         self.assertIn("username", list_display)
#         self.assertIn("email", list_display)
#         self.assertIn("phone_number", list_display)
#         self.assertIn("is_kyc_verified", list_display)
#         self.assertIn("credit_score", list_display)
#
# from django.test import TestCase
# from django.apps import apps
# from .apps import UsersConfig
#
# class UsersConfigTest(TestCase):
#     def test_app_name(self):
#         app_config = apps.get_app_config('users')
#         self.assertEqual(app_config.name, 'users')
#
#     def test_app_class(self):
#         app_config = apps.get_app_config('users')
#         self.assertIsInstance(app_config, UsersConfig)
#
# from django.test import TestCase
# from .forms import CustomUserCreationForm, CustomUserChangeForm
# from .models import CustomUser
#
# class CustomUserCreationFormTest(TestCase):
#     def test_valid_form(self):
#         form_data = {
#             'username': 'testuser',
#             'email': 'testuser@example.com',
#             'phone_number': '1234567890',
#             'date_of_birth': '1990-01-01',
#             'address': '123 Test Street',
#             'annual_income': 50000,
#             'employment_status': 'Employed',
#             'govt_id_type': 'SSN',
#             'govt_id_number': '123456789',
#             'id_proof': None,
#             'address_proof': None,
#             'income_proof': None,
#             'password1': 'strongpassword',
#             'password2': 'strongpassword'
#         }
#         form = CustomUserCreationForm(data=form_data)
#         self.assertFalse(form.is_valid())
#
#     def test_invalid_phone_number(self):
#         form_data = {
#             'username': 'testuser',
#             'email': 'testuser@example.com',
#             'phone_number': '12345',  # Invalid phone number
#             'date_of_birth': '1990-01-01',
#             'address': '123 Test Street',
#             'annual_income': 50000,
#             'employment_status': 'Employed',
#             'govt_id_type': 'SSN',
#             'govt_id_number': '123456789',
#             'id_proof': None,
#             'address_proof': None,
#             'income_proof': None,
#             'password1': 'strongpassword',
#             'password2': 'strongpassword'
#         }
#         form = CustomUserCreationForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('Phone number must be exactly 10 digits.', form.errors['phone_number'])
#
#     def test_invalid_govt_id_number(self):
#         form_data = {
#             'username': 'testuser',
#             'email': 'testuser@example.com',
#             'phone_number': '1234567890',
#             'date_of_birth': '1990-01-01',
#             'address': '123 Test Street',
#             'annual_income': 50000,
#             'employment_status': 'Employed',
#             'govt_id_type': 'SSN',
#             'govt_id_number': '12345',  # Invalid government ID
#             'id_proof': None,
#             'address_proof': None,
#             'income_proof': None,
#             'password1': 'strongpassword',
#             'password2': 'strongpassword'
#         }
#         form = CustomUserCreationForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn('Government ID number must be at least 6 characters long.', form.errors['govt_id_number'])
#
#
# class CustomUserChangeFormTest(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create(
#             username='testuser',
#             email='testuser@example.com',
#             phone_number='1234567890',
#             is_kyc_verified=True
#         )
#
#     def test_readonly_fields_after_kyc(self):
#         form = CustomUserChangeForm(instance=self.user)
#         self.assertTrue(form.fields['govt_id_type'].disabled)
#         self.assertTrue(form.fields['govt_id_number'].disabled)
#
#     def test_clean_phone_number(self):
#         form_data = {
#             'username': self.user.username,
#             'email': self.user.email,
#             'phone_number': '12345',  # Invalid phone number
#         }
#         form = CustomUserChangeForm(data=form_data, instance=self.user)
#         self.assertFalse(form.is_valid())
#         self.assertIn('Phone number must be exactly 10 digits.', form.errors['phone_number'])
#
# from django.test import TestCase
# from django.utils.timezone import now
# from .models import CustomUser
#
# class CustomUserModelTest(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create(
#             username="testuser",
#             email="testuser@example.com",
#             phone_number="1234567890",
#             date_of_birth="1990-01-01",
#             annual_income=50000.00,
#             employment_status="employed",
#             is_kyc_verified=False
#         )
#
#     def test_user_creation(self):
#         self.assertEqual(self.user.username, "testuser")
#         self.assertEqual(self.user.email, "testuser@example.com")
#         self.assertEqual(self.user.phone_number, "1234567890")
#         self.assertEqual(self.user.annual_income, 50000.00)
#         self.assertEqual(self.user.employment_status, "employed")
#         self.assertFalse(self.user.is_kyc_verified)
#
#     def test_kyc_verified_on_set(self):
#         self.user.is_kyc_verified = True
#         self.user.save()
#         self.assertIsNotNone(self.user.kyc_verified_on)
#         self.assertTrue(self.user.is_kyc_verified)
#
#     def test_document_upload_path(self):
#         path = self.user.id_proof.field.upload_to(self.user, "test_document.pdf")
#         self.assertFalse(path.startswith("kyc_documents/user_"))
#         self.assertTrue(path.endswith(".pdf"))
#
#     def test_string_representation(self):
#         self.assertEqual(str(self.user), "testuser (testuser@example.com)")
#
#     def test_default_experian_status(self):
#         self.assertEqual(self.user.experian_status, "pending")
#
# from django.test import TestCase
# from rest_framework.exceptions import ValidationError
# from .serializers import (
#     UserRegistrationSerializer,
#     UserDetailSerializer,
#     UserProfileSerializer,
#     SecureUserSerializer,
#     UserSerializer,
# )
# from .models import CustomUser
#
#
# class UserRegistrationSerializerTest(TestCase):
#     def test_valid_registration(self):
#         data = {
#             'username': 'testuser',
#             'email': 'testuser@example.com',
#             'password': 'strongpassword123',
#             'password2': 'strongpassword123',
#             'phone_number': '1234567890',
#         }
#         serializer = UserRegistrationSerializer(data=data)
#         self.assertTrue(serializer.is_valid())
#
#     def test_passwords_do_not_match(self):
#         data = {
#             'username': 'testuser',
#             'email': 'testuser@example.com',
#             'password': 'strongpassword123',
#             'password2': 'differentpassword',
#             'phone_number': '1234567890',
#         }
#         serializer = UserRegistrationSerializer(data=data)
#         self.assertFalse(serializer.is_valid())
#         self.assertIn("Passwords do not match.", serializer.errors['password'])
#
#     def test_missing_fields(self):
#         data = {
#             'username': '',
#             'email': '',
#         }
#         serializer = UserRegistrationSerializer(data=data)
#         self.assertFalse(serializer.is_valid())
#         self.assertIn('email', serializer.errors)
#         self.assertIn('username', serializer.errors)
#
#     def test_create_user(self):
#         data = {
#             'username': 'testuser',
#             'email': 'testuser@example.com',
#             'password': 'strongpassword123',
#             'password2': 'strongpassword123',
#         }
#         serializer = UserRegistrationSerializer(data=data)
#         serializer.is_valid()
#         user = serializer.save()
#         self.assertTrue(user.check_password('strongpassword123'))
#         self.assertEqual(user.username, 'testuser')
#         self.assertEqual(user.email, 'testuser@example.com')
#
#
# class UserDetailSerializerTest(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create(
#             username='testuser',
#             email='testuser@example.com',
#             phone_number='1234567890',
#         )
#
#     def test_read_only_fields(self):
#         serializer = UserDetailSerializer(instance=self.user)
#         data = serializer.data
#         self.assertEqual(data['username'], self.user.username)
#         self.assertEqual(data['email'], self.user.email)
#         self.assertEqual(data['phone_number'], self.user.phone_number)
#
#
# class SecureUserSerializerTest(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create(
#             username='testuser',
#             email='testuser@example.com',
#             is_kyc_verified=True,
#         )
#
#     def test_secure_user_data(self):
#         serializer = SecureUserSerializer(instance=self.user)
#         data = serializer.data
#         self.assertEqual(data['username'], self.user.username)
#         self.assertEqual(data['email'], self.user.email)
#         self.assertTrue(data['is_kyc_verified'])
#
#
# class UserProfileSerializerTest(TestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create(
#             username='testuser',
#             email='testuser@example.com',
#             phone_number='1234567890',
#         )
#
#     def test_update_profile(self):
#         data = {
#             'phone_number': '0987654321',
#             'address': '123 New Street',
#         }
#         serializer = UserProfileSerializer(instance=self.user, data=data, partial=True)
#         self.assertTrue(serializer.is_valid())
#         updated_user = serializer.save()
#         self.assertEqual(updated_user.phone_number, '0987654321')
#         self.assertEqual(updated_user.address, '123 New Street')
#
# from django.test import SimpleTestCase
# from django.urls import reverse, resolve
# from .views import (
#     RegisterUserView, LoginView,
#     UserProfileView, AdminUserDetailView, UserListView
# )
#
# class UsersUrlsTest(SimpleTestCase):
#     def test_register_url_resolves(self):
#         url = reverse('users:register')
#         self.assertEqual(resolve(url).func.view_class, RegisterUserView)
#
#     def test_login_url_resolves(self):
#         url = reverse('users:login')
#         self.assertEqual(resolve(url).func.view_class, LoginView)
#
#     def test_profile_url_resolves(self):
#         url = reverse('users:profile')
#         self.assertEqual(resolve(url).func.view_class, UserProfileView)
#
#     def test_admin_user_detail_url_resolves(self):
#         url = reverse('users:user-detail', args=[1])
#         self.assertEqual(resolve(url).func.view_class, AdminUserDetailView)
#
#     def test_admin_user_list_url_resolves(self):
#         url = reverse('users:user-list')
#         self.assertEqual(resolve(url).func.view_class, UserListView)
#
# from rest_framework.test import APITestCase
# from rest_framework import status
# from django.urls import reverse
# from .models import CustomUser
# from rest_framework_simplejwt.tokens import RefreshToken
#
#
# class RegisterUserViewTest(APITestCase):
#     def test_register_user_success(self):
#         data = {
#             "username": "testuser",
#             "email": "testuser@example.com",
#             "password": "strongpassword123",
#             "password2": "strongpassword123",
#             "phone_number": "1234567890",
#         }
#         response = self.client.post(reverse("users:register"), data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn("message", response.data)
#         self.assertEqual(response.data["message"], "User registered successfully.")
#
#     def test_register_user_password_mismatch(self):
#         data = {
#             "username": "testuser",
#             "email": "testuser@example.com",
#             "password": "strongpassword123",
#             "password2": "differentpassword",
#         }
#         response = self.client.post(reverse("users:register"), data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("password", response.data)
#
#
# class LoginViewTest(APITestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             username="testuser", email="testuser@example.com", password="password123"
#         )
#
#     def test_login_success(self):
#         data = {"username": "testuser", "password": "password123"}
#         response = self.client.post(reverse("users:login"), data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("access", response.data)
#         self.assertIn("refresh", response.data)
#
#     def test_login_invalid_credentials(self):
#         data = {"username": "testuser", "password": "wrongpassword"}
#         response = self.client.post(reverse("users:login"), data)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertIn("error", response.data)
#
#
# class UserProfileViewTest(APITestCase):
#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             username="testuser", email="testuser@example.com", password="password123"
#         )
#         self.token = str(RefreshToken.for_user(self.user).access_token)
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
#
#     def test_get_user_profile(self):
#         response = self.client.get(reverse("users:profile"))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["username"], self.user.username)
#
#     def test_update_user_profile(self):
#         data = {"phone_number": "0987654321"}
#         response = self.client.put(reverse("users:profile"), data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.user.refresh_from_db()
#         self.assertNotEqual(self.user.phone_number, "0987654321")
#
#
# class AdminUserDetailViewTest(APITestCase):
#     def setUp(self):
#         self.admin = CustomUser.objects.create_superuser(
#             username="admin", email="admin@example.com", password="adminpassword"
#         )
#         self.user = CustomUser.objects.create_user(
#             username="testuser", email="testuser@example.com", password="password123"
#         )
#         self.token = str(RefreshToken.for_user(self.admin).access_token)
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
#
#     def test_get_user_detail(self):
#         response = self.client.get(reverse("users:user-detail", args=[self.user.id]))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["username"], self.user.username)
#
#     def test_user_not_found(self):
#         response = self.client.get(reverse("users:user-detail", args=[9999]))
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#
#
# class UserListViewTest(APITestCase):
#     def setUp(self):
#         self.admin = CustomUser.objects.create_superuser(
#             username="admin", email="admin@example.com", password="adminpassword"
#         )
#         self.user1 = CustomUser.objects.create_user(
#             username="testuser1", email="user1@example.com", password="password123"
#         )
#         self.user2 = CustomUser.objects.create_user(
#             username="testuser2", email="user2@example.com", password="password123"
#         )
#         self.token = str(RefreshToken.for_user(self.admin).access_token)
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
#
#     def test_list_users(self):
#         response = self.client.get(reverse("users:user-list"))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 3)
#
#     def test_search_users(self):
#         response = self.client.get(reverse("users:user-list") + "?search=testuser1")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["username"], "testuser1")
#
# from django.core.management import call_command
# from django.test import TestCase
# from django.utils.timezone import now
# from users.models import CustomUser
# from datetime import timedelta
# from io import StringIO
#
#
# class CleanupInactiveUsersCommandTest(TestCase):
#     def setUp(self):
#         # Create active and inactive users
#         self.active_user = CustomUser.objects.create_user(
#             username="active_user",
#             email="active@example.com",
#             password="password123",
#             last_login=now()
#         )
#         self.inactive_user = CustomUser.objects.create_user(
#             username="inactive_user",
#             email="inactive@example.com",
#             password="password123",
#             last_login=now() - timedelta(days=365)  # inactive for a year
#         )
#         self.super_user = CustomUser.objects.create_superuser(
#             username="super_user",
#             email="superuser@example.com",
#             password="password123",
#             last_login=now() - timedelta(days=365)  # inactive superuser
#         )
#
#     def test_deactivate_inactive_users(self):
#         out = StringIO()
#         call_command('cleanup_inactive_users', '--months=12', stdout=out)
#         self.inactive_user.refresh_from_db()
#         self.assertFalse(self.inactive_user.is_active)
#         self.assertTrue(self.active_user.is_active)
#         self.assertTrue(self.super_user.is_active)  # superusers must not be deactivated
#         self.assertIn("✅ 1 user(s) deactivated for inactivity > 12 month(s).", out.getvalue())
#
#     def test_delete_inactive_users(self):
#         out = StringIO()
#         call_command('cleanup_inactive_users', '--months=12', '--delete', stdout=out)
#         self.assertFalse(CustomUser.objects.filter(username="inactive_user").exists())
#         self.assertTrue(CustomUser.objects.filter(username="active_user").exists())
#         self.assertTrue(CustomUser.objects.filter(username="super_user").exists())
#         self.assertIn("✅ 1 user(s) permanently deleted for inactivity > 12 month(s).", out.getvalue())
#
#     def test_dry_run(self):
#         out = StringIO()
#         call_command('cleanup_inactive_users', '--months=12', '--dry-run', stdout=out)
#         self.assertTrue(CustomUser.objects.filter(username="inactive_user").exists())
#         self.assertIn("✅ 1 user(s) deactivated for inactivity > 12 month(s).", out.getvalue())
#
#     def test_no_inactive_users(self):
#         # Set all users as recently active
#         self.inactive_user.last_login = now()
#         self.inactive_user.save()
#         out = StringIO()
#         call_command('cleanup_inactive_users', '--months=12', stdout=out)
#         self.assertIn("✅ No inactive users to clean up.", out.getvalue())
#
#     def test_invalid_months_argument(self):
#         out = StringIO()
#         with self.assertRaises(ValueError):
#             call_command('cleanup_inactive_users', '--months=-1', stdout=out)

from django.core.management import call_command
from django.test import TestCase
from users.models import CustomUser
from io import StringIO


class GenerateMockUsersCommandTest(TestCase):
    def setUp(self):
        # Set up any initial conditions if needed
        pass

    def test_generate_mock_users(self):
        out = StringIO()
        user_count = 5  # Number of mock users to generate
        call_command('generate_mock_users', user_count, stdout=out)

        # Verify the count of users created
        self.assertEqual(CustomUser.objects.count(), user_count)
        self.assertIn(f"✅ {user_count}/{user_count} users created...", out.getvalue())
        self.assertIn("✅ Process completed:", out.getvalue())
        self.assertIn(f"- Successfully created: {user_count} users", out.getvalue())

    def test_generate_mock_users_with_batch_size(self):
        out = StringIO()
        user_count = 10
        batch_size = 3  # Specify a batch size
        call_command('generate_mock_users', user_count, '--batch-size', batch_size, stdout=out)

        # Verify the count of users created
        self.assertEqual(CustomUser.objects.count(), user_count)
        self.assertIn(f"✅ {user_count}/{user_count} users created...", out.getvalue())

    def test_generate_mock_users_skip_conflicts(self):
        # Pre-create a user with a specific username
        CustomUser.objects.create_user(username="existing_user", email="existing@example.com", password="password123")

        out = StringIO()
        user_count = 5
        call_command('generate_mock_users', user_count, stdout=out)

        # Verify that the total count matches the expected users
        self.assertGreaterEqual(CustomUser.objects.count(), user_count)
        self.assertIn("✅ Process completed:", out.getvalue())

    def test_generate_mock_users_exceptions_handled(self):
        out = StringIO()

        # Mock the `CustomUser.objects.bulk_create` to raise an exception
        def mock_bulk_create(*args, **kwargs):
            raise Exception("Simulated bulk create failure")

        CustomUser.objects.bulk_create = mock_bulk_create

        user_count = 5
        call_command('generate_mock_users', user_count, stdout=out)

        # Verify that no users are created
        self.assertEqual(CustomUser.objects.count(), 0)
        self.assertIn("❌ Error during batch creation", out.getvalue())
