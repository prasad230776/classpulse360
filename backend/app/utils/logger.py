import contextvars
import logging
import logging.config
import os
from app.core.config import settings

# Thread-safe ContextVar to hold current request ID (for future HTTP logging middleware compatibility)
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class RequestIDFilter(logging.Filter):
    """
    Filter to inject contextvar-stored request_id into each logging record.
    """

    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


def setup_logging():
    """
    Initializes centralized structured logging.
    - Console Output: Configured for all environments (verbose in development).
    - File Output: Appends to rotating files (logs/app.log) in staging/production.
    """
    log_level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO

    # Create local logs folder inside the project root workspace directory
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id_filter": {
                "()": RequestIDFilter,
            }
        },
        "formatters": {
            "standard": {
                "format": "[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(name)s:%(lineno)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "[%(asctime)s] [%(levelname)s] [%(request_id)s] [%(process)d:%(threadName)s] [%(name)s:%(lineno)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "filters": ["request_id_filter"],
            },
            "file": {
                "level": logging.INFO,
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(log_dir, "app.log"),
                "maxBytes": 5 * 1024 * 1024,  # 5 Megabytes
                "backupCount": 5,
                "formatter": "detailed",
                "filters": ["request_id_filter"],
                "encoding": "utf8",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"]
                if settings.ENVIRONMENT in ["production", "staging"]
                else ["console"],
                "level": log_level,
                "propagate": True,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": logging.WARNING,
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(log_config)
