import uuid
import string
from app.utils.strings import generate_random_string


def generate_uuid() -> uuid.UUID:
    """
    Generates a standard random version 4 UUID.
    """
    return uuid.uuid4()


def generate_room_code(length: int = 6) -> str:
    """
    Generates a randomized uppercase alphanumeric room code.
    Suitable for session joining codes (e.g. "AB12CD").
    """
    return generate_random_string(length, chars=string.ascii_uppercase + string.digits)
