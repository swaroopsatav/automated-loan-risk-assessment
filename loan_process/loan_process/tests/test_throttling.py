"""
Tests for the rate limiting functionality.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class ThrottlingTest(TestCase):
    """Test case for rate limiting functionality."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create an API client
        self.client = APIClient()
        
        # URLs for testing
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        
    def test_login_throttling(self):
        """Test that login endpoint is rate limited."""
        # Make multiple requests to trigger throttling
        for i in range(6):  # AuthRateThrottle is set to 5/minute
            response = self.client.post(
                self.login_url,
                {'username': 'testuser', 'password': 'wrongpassword'},
                format='json'
            )
            
            # The first 5 requests should return 401 (Unauthorized)
            if i < 5:
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            else:
                # The 6th request should be throttled (429 Too Many Requests)
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                self.assertIn('Request was throttled', response.data['detail'])
    
    def test_register_throttling(self):
        """Test that register endpoint is rate limited."""
        # Make multiple requests to trigger throttling
        for i in range(11):  # BurstRateThrottle is set to 10/minute
            response = self.client.post(
                self.register_url,
                {
                    'username': f'newuser{i}',
                    'email': f'newuser{i}@example.com',
                    'password': 'password123',
                    'password_confirm': 'password123'
                },
                format='json'
            )
            
            # The first 10 requests should return 201 (Created) or 400 (Bad Request)
            if i < 10:
                self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
            else:
                # The 11th request should be throttled (429 Too Many Requests)
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                self.assertIn('Request was throttled', response.data['detail'])
    
    def test_authenticated_throttling(self):
        """Test that authenticated endpoints are rate limited."""
        # Login the user
        self.client.force_authenticate(user=self.user)
        
        # URL for a sensitive endpoint (e.g., loan application creation)
        loan_create_url = reverse('loan-create')
        
        # Make multiple requests to trigger throttling
        for i in range(11):  # SensitiveEndpointThrottle is set to 10/hour
            response = self.client.post(
                loan_create_url,
                {
                    'amount_requested': 5000,
                    'purpose': 'Test loan',
                    'term_months': 12
                },
                format='json'
            )
            
            # The first 10 requests should not be throttled
            if i < 10:
                self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
            else:
                # The 11th request should be throttled (429 Too Many Requests)
                self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                self.assertIn('Request was throttled', response.data['detail'])