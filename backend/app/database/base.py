from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy 2.0 ORM models.
    All models in app/models/ should inherit from this class.
    """
    pass
