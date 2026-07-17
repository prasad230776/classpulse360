import logging
from typing import Dict, Any
import jwt
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate
from app.models.user import User
from app.services.user_service import user_service
from app.repositories.user_repository import user_repository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.exceptions import ResourceNotFoundException, BusinessRuleException

logger = logging.getLogger(__name__)


class AuthService:
    """
    Business service layer managing user registration, logins, token renewals, and credentials verification.
    """

    def register(self, db: Session, *, user_in: UserCreate) -> User:
        """
        Register a new user profile by delegating creation to UserService.
        """
        logger.info(f"Auth register requesting new user: {user_in.username}")
        return user_service.create_user(db, obj_in=user_in)

    def login(self, db: Session, *, username_or_email: str, password: str) -> Dict[str, str]:
        """
        Logs in a user, returning access and refresh JWT tokens.
        """
        user = self.verify_credentials(db, username_or_email=username_or_email, password=password)
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def verify_credentials(self, db: Session, *, username_or_email: str, password: str) -> User:
        """
        Verifies if username/email and passwords match existing records.
        """
        # Try checking by email first
        user = user_repository.get_by_email(db, email=username_or_email)
        if not user:
            # Check by username
            user = user_repository.get_by_username(db, username=username_or_email)

        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {username_or_email}")
            raise BusinessRuleException(
                "Incorrect username/email or password.", code="INVALID_CREDENTIALS"
            )

        if not user.is_active:
            raise BusinessRuleException("User account is currently inactive.", code="INACTIVE_USER")

        logger.info(f"User {user.username} verified successfully.")
        return user

    def refresh_token(self, db: Session, *, refresh_token: str) -> Dict[str, str]:
        """
        Decodes a refresh token, validates subject context, and issues a new access token.
        """
        try:
            payload = decode_token(refresh_token)
            user_id = payload.get("sub")
            token_type = payload.get("type")
            if not user_id or token_type != "refresh":
                raise BusinessRuleException(
                    "Invalid token payload or type.", code="INVALID_TOKEN"
                )
        except jwt.PyJWTError:
            raise BusinessRuleException(
                "Token signature check or format validation failed.", code="INVALID_TOKEN"
            )

        user = user_repository.get_by_id(db, id=user_id)
        if not user:
            raise ResourceNotFoundException("User", user_id)
        if not user.is_active:
            raise BusinessRuleException("User account is currently inactive.", code="INACTIVE_USER")

        new_access = create_access_token(user.id)
        return {"access_token": new_access, "token_type": "bearer"}

    def change_password(self, db: Session, *, user: User, old_password: str, new_password: str) -> User:
        """
        Validates old credentials and updates the password.
        """
        if not verify_password(old_password, user.hashed_password):
            raise BusinessRuleException("Incorrect current password.", code="INCORRECT_PASSWORD")
        logger.info(f"User {user.username} updating account password.")
        return user_repository.update_password(db, user=user, password=new_password)


auth_service = AuthService()
