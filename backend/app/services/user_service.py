import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import user_repository
from app.repositories.institution_repository import institution_repository
from app.exceptions import ResourceNotFoundException, ResourceAlreadyExistsException

logger = logging.getLogger(__name__)


class UserService:
    """
    Business service layer managing User profiles and account states.
    """

    def get_user(self, db: Session, user_id: UUID) -> User:
        """
        Fetch a user by their UUID.
        """
        user = user_repository.get_by_id(db, user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        return user

    def get_user_by_username(self, db: Session, username: str) -> User:
        """
        Fetch a user by their unique username.
        """
        user = user_repository.get_by_username(db, username)
        if not user:
            raise ResourceNotFoundException("User", username)
        return user

    def get_user_by_email(self, db: Session, email: str) -> User:
        """
        Fetch a user by their unique email.
        """
        user = user_repository.get_by_email(db, email)
        if not user:
            raise ResourceNotFoundException("User", email)
        return user

    def list_users(self, db: Session, *, offset: int = 0, limit: int = 100) -> List[User]:
        """
        List users with offset/limit pagination.
        """
        return user_repository.get_all(db, offset=offset, limit=limit)

    def count_users(self, db: Session) -> int:
        """
        Count total users registered.
        """
        return user_repository.count(db)

    def create_user(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Register a new user profile, validating uniqueness constraints and institution linkage.
        """
        # Validate Institution if provided
        if obj_in.institution_id:
            if not institution_repository.exists(db, obj_in.institution_id):
                raise ResourceNotFoundException("Institution", obj_in.institution_id)

        # Validate Username uniqueness
        if user_repository.username_exists(db, obj_in.username):
            logger.warning(f"Registration failure: Username '{obj_in.username}' is already taken.")
            raise ResourceAlreadyExistsException("User", "username", obj_in.username)

        # Validate Email uniqueness
        if user_repository.email_exists(db, obj_in.email):
            logger.warning(f"Registration failure: Email '{obj_in.email}' is already registered.")
            raise ResourceAlreadyExistsException("User", "email", obj_in.email)

        logger.info(f"Creating user profile: {obj_in.username} ({obj_in.email})")
        return user_repository.create_user(db, obj_in=obj_in)

    def update_user(self, db: Session, *, user_id: UUID, obj_in: UserUpdate) -> User:
        """
        Update user profile.
        """
        db_obj = self.get_user(db, user_id)

        # If changing username, check uniqueness
        if obj_in.username and obj_in.username != db_obj.username:
            if user_repository.username_exists(db, obj_in.username):
                raise ResourceAlreadyExistsException("User", "username", obj_in.username)

        # If changing email, check uniqueness
        if obj_in.email and obj_in.email != db_obj.email:
            if user_repository.email_exists(db, obj_in.email):
                raise ResourceAlreadyExistsException("User", "email", obj_in.email)

        logger.info(f"Updating user profile {user_id}")
        return user_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def activate_user(self, db: Session, *, user_id: UUID) -> User:
        """
        Set a user's status to active.
        """
        user = self.get_user(db, user_id)
        logger.info(f"Activating user account: {user_id}")
        return user_repository.activate_user(db, user=user)

    def delete_user(self, db: Session, *, user_id: UUID) -> User:
        """
        Delete a user profile.
        """
        self.get_user(db, user_id)
        logger.info(f"Deleting user account: {user_id}")
        return user_repository.delete(db, id=user_id)


user_service = UserService()
