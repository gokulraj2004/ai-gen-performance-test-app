"""
Rate limiting middleware using slowapi.

Applies rate limits to authentication endpoints to prevent
brute-force and credential stuffing attacks.
"""
from fastapi import FastAPI

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

    def setup_rate_limiting(app: FastAPI) -> None:
        """Configure rate limiting middleware on the FastAPI application."""
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)

except ImportError:
    # slowapi not installed — provide a no-op setup
    limiter = None  # type: ignore

    def setup_rate_limiting(app: FastAPI) -> None:
        """No-op: slowapi is not installed."""
        pass