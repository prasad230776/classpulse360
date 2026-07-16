from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SubjectBase(BaseModel):
    """
    Base Pydantic schema for a Subject, containing common attributes.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Unique, descriptive name of the subject.")
    code: Optional[str] = Field(None, max_length=20, description="Unique alphanumeric identifier code for the subject.")
    description: Optional[str] = Field(None, description="Detailed description/syllabus summary.")
    is_active: bool = Field(True, description="Flag indicating if the subject is active.")


class SubjectCreate(SubjectBase):
    """
    Schema for creating a new Subject.
    """
    pass


class SubjectUpdate(BaseModel):
    """
    Schema for updating an existing Subject. All fields are optional.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SubjectResponse(SubjectBase):
    """
    Response schema returning complete Subject details, including database-generated values.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the subject.")
    created_at: datetime = Field(..., description="Timestamp when the subject was registered.")
    updated_at: datetime = Field(..., description="Timestamp when the subject was last updated.")


class SubjectListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of subjects.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[SubjectResponse] = Field(..., description="List of subjects matching criteria.")
    total: int = Field(..., description="Total count of subjects available.")
