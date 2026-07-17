from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.utils import setup_logging

from app.api.router import api_router
from app.api.exception_handlers import register_exception_handlers
from app.api.middlewares import (
    RequestIDMiddleware,
    RequestTimingMiddleware,
    RequestLoggingMiddleware,
)
from app.websockets import websocket_router

# Configure Centralized Logging
setup_logging()

# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set CORS middleware (essential for frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register middlewares (bottom-to-top nested wrapping)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Register central routers
app.include_router(api_router, prefix="/api")
app.include_router(websocket_router)

# Register global exception handlers
register_exception_handlers(app)


@app.get("/health", tags=["Health"])
def health_check():
    """
    Simple health check endpoint to verify that the API is up and running.
    """
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }
