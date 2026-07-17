import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserUpdate
from app.common.enums import UserRole, UserStatus
from app.core.security import verify_password


def test_create_user(db: Session):
    """
    Test creating a user with custom password mapping.
    """
    obj_in = UserCreate(
        name="John Doe",
        username="johndoe",
        email="john@example.com",
        password="secretpassword",
        role=UserRole.STUDENT,
        status=UserStatus.APPROVED
    )
    db_obj = user_repository.create_user(db, obj_in=obj_in)
    assert db_obj.id is not None
    assert db_obj.username == "johndoe"
    assert verify_password("secretpassword", db_obj.hashed_password)


def test_user_email_and_username_exists(db: Session):
    """
    Test specialized lookup methods.
    """
    email = "test@example.com"
    username = "testuser"

    assert not user_repository.email_exists(db, email)
    assert not user_repository.username_exists(db, username)

    obj_in = UserCreate(
        name="Test User",
        username=username,
        email=email,
        password="password123",
        role=UserRole.TEACHER
    )
    user_repository.create_user(db, obj_in=obj_in)

    assert user_repository.email_exists(db, email)
    assert user_repository.username_exists(db, username)

    fetched_by_email = user_repository.get_by_email(db, email)
    assert fetched_by_email is not None
    assert fetched_by_email.username == username

    fetched_by_user = user_repository.get_by_username(db, username)
    assert fetched_by_user is not None
    assert fetched_by_user.email == email


def test_duplicate_user_registration_fails(db: Session):
    """
    Test constraint validation on duplicate username.
    """
    user_in = UserCreate(
        name="User One",
        username="duplicateuser",
        email="one@example.com",
        password="password1"
    )
    user_repository.create_user(db, obj_in=user_in)

    # Creating user with same username should fail
    duplicate_in = UserCreate(
        name="User Two",
        username="duplicateuser",
        email="two@example.com",
        password="password二"
    )

    with pytest.raises(IntegrityError):
        user_repository.create_user(db, obj_in=duplicate_in)


def test_update_password_and_activate(db: Session):
    """
    Test password update and activation helpers.
    """
    user_in = UserCreate(
        name="State Change User",
        username="stateuser",
        email="state@example.com",
        password="oldpassword",
        is_active=False
    )
    db_obj = user_repository.create_user(db, obj_in=user_in)
    assert not db_obj.is_active

    # Activate
    activated_user = user_repository.activate_user(db, user=db_obj)
    assert activated_user.is_active

    # Update password
    updated_user = user_repository.update_password(db, user=activated_user, password="newpassword")
    assert verify_password("newpassword", updated_user.hashed_password)
