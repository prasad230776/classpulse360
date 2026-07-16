from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.common.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """
    Base Pydantic schema for a User, containing common user profile attributes.
    """
    institution_id: Optional[UUID] = Field(None, description="Associated institution UUID.")
    role: UserRole = Field(UserRole.STUDENT, description="Application role of the user.")
    status: UserStatus = Field(UserStatus.PENDING, description="Approval status of the user's account.")
    name: str = Field(..., min_length=2, max_length=150, description="Full name of the user.")
    username: str = Field(
        ...,
        min_length=4,
        max_length=30,
        pattern="^[A-Za-z0-9._]+$",
        description="Unique username containing letters, numbers, dots, or underscores."
    )
    email: EmailStr = Field(..., description="Unique user email address.")
    mobile_number: Optional[str] = Field(None, max_length=20, description="Contact phone number.")
    roll_number: Optional[str] = Field(None, max_length=50, description="Student academic roll number if applicable.")
    employee_id: Optional[str] = Field(None, max_length=50, description="Teacher/Staff employee ID if applicable.")
    avatar_url: Optional[str] = Field(None, description="URL to user profile image.")
    is_active: bool = Field(True, description="Flag indicating if the user account is active.")


class UserCreate(UserBase):
    """
    Schema for registering/creating a new user. Includes password credentials.
    """
    password: str = Field(..., min_length=8, max_length=100, description="Plaintext password (hashed before insertion).")


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user's profile information. All fields are optional.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    username: Optional[str] = Field(None, min_length=4, max_length=30, pattern="^[A-Za-z0-9._]+$")
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = Field(None, max_length=20)
    roll_number: Optional[str] = Field(None, max_length=50)
    employee_id: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    Response schema returning User details. Strictly excludes password credentials.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the user.")
    last_login: Optional[datetime] = Field(None, description="Timestamp of user's last successful login.")
    created_at: datetime = Field(..., description="Timestamp when the user account was created.")
    updated_at: datetime = Field(..., description="Timestamp when the user account was last modified.")


class UserListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of users.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[UserResponse] = Field(..., description="List of users matching criteria.")
    total: int = Field(..., description="Total count of users available.")
