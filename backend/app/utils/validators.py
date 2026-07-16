import re

# Standard regex patterns
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 phone number format


def validate_email_format(email: str) -> bool:
    """
    Validates if a string adheres to standard email formatting structure.
    """
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))


def validate_phone_format(phone: str) -> bool:
    """
    Validates if a phone string matches the standard international E.164 phone specification.
    """
    if not phone:
        return False
    return bool(PHONE_REGEX.match(phone))
