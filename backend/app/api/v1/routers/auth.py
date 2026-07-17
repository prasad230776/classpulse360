from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.api.responses import APIResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import auth_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.models.user import User

auth_router = APIRouter()


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh JWT token")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=8, description="Current password")
    new_password: str = Field(..., min_length=8, description="New secure password")


@auth_router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new student, teacher, or administrator account.
    """
    db_obj = auth_service.register(db, user_in=user_in)
    return APIResponse(
        success=True,
        message="User profile registered successfully.",
        data=UserResponse.model_validate(db_obj),
    )


@auth_router.post(
    "/login",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and return tokens",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, accepts username/email and password.
    Returns access and refresh JWT tokens.
    """
    tokens = auth_service.login(
        db, username_or_email=form_data.username, password=form_data.password
    )
    return APIResponse(
        success=True,
        message="User authenticated successfully.",
        data=tokens,
    )


@auth_router.post(
    "/refresh",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
def refresh(payload: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Renew an expired access token using a valid refresh token.
    """
    new_token = auth_service.refresh_token(db, refresh_token=payload.refresh_token)
    return APIResponse(
        success=True,
        message="Access token refreshed successfully.",
        data=new_token,
    )


@auth_router.post(
    "/logout",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Log out user",
)
def logout(current_user: User = Depends(get_current_user)):
    """
    Log out the current user session (client should discard the JWTs).
    """
    return APIResponse(
        success=True,
        message="Logged out successfully.",
    )


@auth_router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Return profile data of the currently authenticated user.
    """
    return APIResponse(
        success=True,
        message="User profile retrieved successfully.",
        data=UserResponse.model_validate(current_user),
    )


@auth_router.post(
    "/change-password",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Change user password",
)
def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update password for the currently logged-in user account.
    """
    auth_service.change_password(
        db,
        user=current_user,
        old_password=payload.old_password,
        new_password=payload.new_password,
    )
    return APIResponse(
        success=True,
        message="Password updated successfully.",
    )
