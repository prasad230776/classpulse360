from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from app.database.engine import engine

# Create the session maker bound to our SQLAlchemy engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator that yields a database session.
    Ensures that the database session is closed after the request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
