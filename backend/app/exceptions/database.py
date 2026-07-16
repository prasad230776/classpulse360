from app.exceptions.base import AppException


class DatabaseException(AppException):
    """
    Base exception for database failures.
    """

    def __init__(self, message: str, code: str = "DATABASE_ERROR"):
        super().__init__(message, code=code)


class DatabaseConnectionError(DatabaseException):
    """
    Raised when connection to the remote database fails.
    """

    def __init__(self, message: str = "Failed to connect to the database."):
        super().__init__(message, code="DATABASE_CONNECTION_FAILED")


class DatabaseTransactionError(DatabaseException):
    """
    Raised when a transaction fails to commit or roll back.
    """

    def __init__(self, message: str = "A database transaction error occurred."):
        super().__init__(message, code="DATABASE_TRANSACTION_FAILED")
