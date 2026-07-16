import re
import string
import random


def slugify(text: str) -> str:
    """
    Simplifies a string to a lowercase, hyphen-separated alphanumeric slug.
    For example: "Intro to Python 101!" -> "intro-to-python-101"
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def generate_random_string(
    length: int = 8, chars: str = string.ascii_letters + string.digits
) -> str:
    """
    Generates a cryptographically secure random string of specified length.
    """
    return "".join(random.SystemRandom().choice(chars) for _ in range(length))
