from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """
    Returns the current datetime in timezone-aware UTC format.
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str:
    """
    Converts a datetime object to a formatted string.
    """
    return dt.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> datetime:
    """
    Parses a formatted string into a datetime object.
    """
    return datetime.strptime(dt_str, fmt)
