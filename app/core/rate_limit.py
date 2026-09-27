"""
Global rate limiter using slowapi (a thin wrapper around the `limits` library).
Keyed by client IP by default; the login endpoint gets a stricter limit to
slow down credential-stuffing / brute force attempts.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_default])
