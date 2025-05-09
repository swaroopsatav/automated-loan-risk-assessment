"""
Custom throttling classes for rate limiting API endpoints.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class BurstRateThrottle(AnonRateThrottle):
    """
    Throttle for short bursts of requests.
    Limits anonymous users to 10 requests per minute.
    """
    scope = 'burst'
    rate = '10/minute'

class SustainedRateThrottle(AnonRateThrottle):
    """
    Throttle for sustained request patterns.
    Limits anonymous users to 100 requests per day.
    """
    scope = 'sustained'
    rate = '100/day'

class AuthRateThrottle(AnonRateThrottle):
    """
    Throttle for authentication endpoints.
    Limits to 5 requests per minute to prevent brute force attacks.
    """
    scope = 'auth'
    rate = '5/minute'

class UserBurstRateThrottle(UserRateThrottle):
    """
    Throttle for short bursts of requests from authenticated users.
    Limits authenticated users to 30 requests per minute.
    """
    scope = 'user_burst'
    rate = '30/minute'

class UserSustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained request patterns from authenticated users.
    Limits authenticated users to 1000 requests per day.
    """
    scope = 'user_sustained'
    rate = '1000/day'

class SensitiveEndpointThrottle(UserRateThrottle):
    """
    Throttle for sensitive endpoints like loan applications.
    Limits authenticated users to 10 requests per hour.
    """
    scope = 'sensitive'
    rate = '10/hour'