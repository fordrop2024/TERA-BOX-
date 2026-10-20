"""
TeraBox Connector Exceptions
============================
Custom exceptions for authentication, network, rate limiting, and expired links.
"""

class TeraBoxError(Exception):
    """Base exception for all TeraBox connector errors."""
    pass


class TeraBoxAuthError(TeraBoxError):
    """Raised when authentication credentials (NDUS cookie / token) are missing or invalid."""
    pass


class TeraBoxNetworkError(TeraBoxError):
    """Raised when network timeout or connection failure occurs."""
    pass


class TeraBoxRateLimitError(TeraBoxError):
    """Raised when TeraBox returns HTTP 429 or rate limit errno."""
    pass


class TeraBoxLinkExpiredError(TeraBoxError):
    """Raised when a share link or download ticket is no longer valid or has expired."""
    pass
