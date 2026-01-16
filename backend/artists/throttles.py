"""
Custom throttle classes for rate limiting API endpoints.

Search endpoints are computationally expensive (Weaviate vector queries),
so they have stricter rate limits than general browsing endpoints.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class SearchAnonThrottle(AnonRateThrottle):
    """Stricter rate limit for anonymous users on search endpoints."""
    scope = 'search'


class SearchUserThrottle(UserRateThrottle):
    """Rate limit for authenticated users on search endpoints."""
    scope = 'search_user'
