from app.exceptions.base import AppException


class ValidationException(AppException):
    """
    Base exception for validation errors.
    """

    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, code=code)


class MCQOptionsInvalidException(ValidationException):
    """
    Raised when options or correct answers format for an MCQ question is incorrect.
    """

    def __init__(self, message: str = "MCQ questions must include a choices option structure."):
        super().__init__(message, code="MCQ_OPTIONS_INVALID")
