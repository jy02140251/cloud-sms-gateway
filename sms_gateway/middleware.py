"""Middleware components for the SMS Gateway API."""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)

        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > cutoff
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
            )

        self._requests[client_ip].append(now)
        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all incoming HTTP requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status={response.status_code} duration={process_time:.3f}s"
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Simple API key authentication middleware."""

    def __init__(self, app, api_keys: list = None, exclude_paths: list = None):
        super().__init__(app)
        self.api_keys = set(api_keys or [])
        self.exclude_paths = set(exclude_paths or ["/health", "/docs", "/openapi.json"])

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in self.api_keys:
            return Response(
                content='{"error": "Invalid or missing API key"}',
                status_code=401,
                media_type="application/json",
            )
        return await call_next(request)