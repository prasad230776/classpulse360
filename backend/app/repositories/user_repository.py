from typing import Optional, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository(BaseRepository[User]):
    """
    Repository class providing specialized database operations for the User model.
    """

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Fetch a user by their email address.
        """
        stmt = select(User).where(User.email == email)
        return db.scalars(stmt).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Fetch a user by their unique username.
        """
        stmt = select(User).where(User.username == username)
        return db.scalars(stmt).first()

    def email_exists(self, db: Session, email: str) -> bool:
        """
        Check if an email address is already registered.
        """
        stmt = select(func.count()).select_from(User).where(User.email == email)
        return db.scalar(stmt) > 0

    def username_exists(self, db: Session, username: str) -> bool:
        """
        Check if a username is already taken.
        """
        stmt = select(func.count()).select_from(User).where(User.username == username)
        return db.scalar(stmt) > 0

    def create_user(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create a new user, mapping the schema's password to the model's hashed_password.
        Note: True cryptography/hashing will be integrated during the Auth phase.
        """
        user_data = obj_in.model_dump(exclude={"password"})
        # Placeholder hashing until Auth phase is implemented
        user_data["hashed_password"] = f"hash_placeholder_{obj_in.password}"

        db_obj = self.model(**user_data)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except Exception:
            db.rollback()
            raise
        return db_obj

    def update_password(self, db: Session, *, user: User, password: str) -> User:
        """
        Update a user's password.
        """
        user.hashed_password = f"hash_placeholder_{password}"
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise
        return user

    def activate_user(self, db: Session, *, user: User) -> User:
        """
        Activate a user's account.
        """
        user.is_active = True
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise
        return user


# Instantiate user repository to be imported elsewhere
user_repository = UserRepository()
