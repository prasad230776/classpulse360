from app.exceptions.base import AppException


class BusinessRuleException(AppException):
    """
    Base exception for business logic and rule violations.
    """

    def __init__(self, message: str, code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(message, code=code)


class InvalidSessionStateException(BusinessRuleException):
    """
    Raised when an operation is invalid for the session's current status.
    """

    def __init__(self, message: str):
        super().__init__(message, code="INVALID_SESSION_STATE")


class AnswerChangeNotAllowedException(BusinessRuleException):
    """
    Raised when a student attempts to update an answer response but the quiz settings lock it.
    """

    def __init__(self, message: str = "This quiz session does not allow changing submitted answers."):
        super().__init__(message, code="ANSWER_CHANGE_LOCKED")
