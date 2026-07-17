import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.responses import APIResponse
from app.exceptions import (
    AppException,
    DatabaseException,
    BusinessRuleException,
    ValidationException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Registers global exception handlers to map custom domain exceptions
    into standardized APIResponses with appropriate HTTP status codes.
    """

    @app.exception_handler(ResourceNotFoundException)
    async def resource_not_found_handler(request: Request, exc: ResourceNotFoundException):
        response = APIResponse(
            success=False,
            message=exc.message,
            metadata={"code": exc.code}
        )
        return JSONResponse(status_code=404, content=response.model_dump())

    @app.exception_handler(ResourceAlreadyExistsException)
    async def resource_already_exists_handler(request: Request, exc: ResourceAlreadyExistsException):
        response = APIResponse(
            success=False,
            message=exc.message,
            metadata={"code": exc.code}
        )
        return JSONResponse(status_code=400, content=response.model_dump())

    @app.exception_handler(BusinessRuleException)
    async def business_rule_handler(request: Request, exc: BusinessRuleException):
        response = APIResponse(
            success=False,
            message=exc.message,
            metadata={"code": exc.code}
        )
        return JSONResponse(status_code=400, content=response.model_dump())

    @app.exception_handler(ValidationException)
    async def validation_handler(request: Request, exc: ValidationException):
        response = APIResponse(
            success=False,
            message=exc.message,
            metadata={"code": exc.code}
        )
        return JSONResponse(status_code=422, content=response.model_dump())

    @app.exception_handler(DatabaseException)
    async def database_handler(request: Request, exc: DatabaseException):
        # Log the detailed query / transaction failure internally
        logger.error(f"Internal Database Failure: {exc.message}", exc_info=True)
        # Redact raw queries/details from the external consumer
        response = APIResponse(
            success=False,
            message="A secure database transaction failure occurred.",
            metadata={"code": "DATABASE_ERROR"}
        )
        return JSONResponse(status_code=500, content=response.model_dump())

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.error(f"Base Application Failure: {exc.message}", exc_info=True)
        response = APIResponse(
            success=False,
            message=exc.message,
            metadata={"code": exc.code}
        )
        return JSONResponse(status_code=500, content=response.model_dump())
