import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logger import request_id_var

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures every incoming request has a unique Request ID.
    Binds the ID to contextvars so that log entries are traceable.
    """

    async def dispatch(self, request: Request, call_next):
        # Extract existing trace ID from request headers or generate a new UUID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Bind to logger contextvar
        token = request_id_var.set(request_id)

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Revert context variable back to default state
            request_id_var.reset(token)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that tracks the exact execution duration of each HTTP request
    and appends a header indicating the transaction time.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}s"
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that performs structured entry/exit logging for each HTTP transaction.
    """

    async def dispatch(self, request: Request, call_next):
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        logger.info(f"Incoming HTTP Request: {method} {path} | Client IP: {client_ip}")

        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time

        logger.info(
            f"Outgoing HTTP Response: {method} {path} | Status: {response.status_code} | Duration: {duration:.4f}s"
        )
        return response
