import pytest
from sqlalchemy.orm import Session
from app.database.engine import engine
from app.database.session import SessionLocal


@pytest.fixture(scope="function")
def db() -> Session:
    """
    Fixture that provides an isolated database session per test.
    Wraps the execution in a transaction and rolls it back at the end
    to ensure tests are fast, correct, and do not pollute the database.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
