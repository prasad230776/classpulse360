from typing import Any
from app.exceptions.base import AppException


class ResourceException(AppException):
    """
    Base exception for resource and mapping failures.
    """

    def __init__(self, message: str, code: str = "RESOURCE_ERROR"):
        super().__init__(message, code=code)


class ResourceNotFoundException(ResourceException):
    """
    Raised when a requested database row/resource is missing.
    """

    def __init__(self, resource_name: str, identifier: Any):
        self.resource_name = resource_name
        self.identifier = identifier
        message = f"{resource_name} with identifier '{identifier}' was not found."
        super().__init__(message, code="RESOURCE_NOT_FOUND")


class ResourceAlreadyExistsException(ResourceException):
    """
    Raised when attempting to create a resource with conflict values (e.g. duplicate keys).
    """

    def __init__(self, resource_name: str, field_name: str, value: Any):
        self.resource_name = resource_name
        self.field_name = field_name
        self.value = value
        message = f"{resource_name} with {field_name} '{value}' already exists."
        super().__init__(message, code="RESOURCE_ALREADY_EXISTS")
