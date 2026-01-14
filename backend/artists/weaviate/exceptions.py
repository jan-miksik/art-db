"""Custom exceptions for Weaviate operations."""


class WeaviateException(Exception):
    """Base exception for Weaviate-related errors."""
    pass


class WeaviateConnectionError(WeaviateException):
    """Raised when connection to Weaviate fails."""
    pass


class WeaviateImageError(WeaviateException):
    """Raised when image processing or validation fails."""
    pass


class WeaviateSecurityError(WeaviateException):
    """Raised when security validation fails (e.g., SSRF protection)."""
    pass
