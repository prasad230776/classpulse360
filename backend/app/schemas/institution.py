from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from app.common.enums import InstitutionType


class InstitutionBase(BaseModel):
    """
    Base Pydantic schema for an Institution, containing common attributes.
    """
    code: str = Field(
        ...,
        min_length=2,
        max_length=20,
        pattern="^[A-Za-z0-9_-]+$",
        description="Unique identifier code for the institution, alphanumeric with dashes/underscores."
    )
    name: str = Field(..., min_length=2, max_length=200, description="Full name of the institution.")
    short_name: Optional[str] = Field(None, max_length=50, description="Optional abbreviated name.")
    institution_type: InstitutionType = Field(..., description="The type/category of the institution.")
    email: Optional[EmailStr] = Field(None, description="Primary contact email address.")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone number.")
    website: Optional[str] = Field(None, max_length=255, description="Website URL.")
    logo_url: Optional[str] = Field(None, description="URL pointing to the institution's logo.")
    address: Optional[str] = Field(None, description="Physical address description.")
    city: Optional[str] = Field(None, max_length=100, description="City name.")
    state: Optional[str] = Field(None, max_length=100, description="State/Province name.")
    country: Optional[str] = Field(None, max_length=100, description="Country name.")
    is_active: bool = Field(True, description="Flag indicating if the institution is active.")


class InstitutionCreate(InstitutionBase):
    """
    Schema for creating a new Institution.
    """
    pass


class InstitutionUpdate(BaseModel):
    """
    Schema for updating an existing Institution. All fields are optional.
    """
    code: Optional[str] = Field(None, min_length=2, max_length=20, pattern="^[A-Za-z0-9_-]+$")
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    short_name: Optional[str] = Field(None, max_length=50)
    institution_type: Optional[InstitutionType] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class InstitutionResponse(InstitutionBase):
    """
    Response schema returning complete Institution details, including database-generated values.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the institution.")
    created_at: datetime = Field(..., description="Timestamp when the institution was registered.")
    updated_at: datetime = Field(..., description="Timestamp when the institution was last updated.")


class InstitutionListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of institutions.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[InstitutionResponse] = Field(..., description="List of institutions matching criteria.")
    total: int = Field(..., description="Total count of institutions available.")
