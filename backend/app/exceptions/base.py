class AppException(Exception):
    """
    Base exception for all application-specific errors.
    All custom domain exceptions must inherit from this class.
    """

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)
