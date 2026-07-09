"""Custom throttle classes for sensitive auth endpoints."""
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Tight per-IP limit on login attempts to mitigate brute force."""

    scope = "login"


class PasswordResetRateThrottle(AnonRateThrottle):
    """Limit password reset requests to prevent OTP spam."""

    scope = "password_reset"
