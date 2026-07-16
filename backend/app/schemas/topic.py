from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TopicBase(BaseModel):
    """
    Base Pydantic schema for a Topic within a Subject, containing common attributes.
    """
    subject_id: UUID = Field(..., description="UUID of the parent subject.")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the topic.")
    code: Optional[str] = Field(None, max_length=20, description="Optional code identifier for the topic.")
    description: Optional[str] = Field(None, description="Detailed description of topic coverage.")
    is_active: bool = Field(True, description="Flag indicating if the topic is active.")


class TopicCreate(TopicBase):
    """
    Schema for creating a new Topic.
    """
    pass


class TopicUpdate(BaseModel):
    """
    Schema for updating an existing Topic. All fields are optional.
    """
    subject_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TopicResponse(TopicBase):
    """
    Response schema returning complete Topic details, including database-generated values.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the topic.")
    created_at: datetime = Field(..., description="Timestamp when the topic was created.")
    updated_at: datetime = Field(..., description="Timestamp when the topic was last updated.")


class TopicListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of topics.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[TopicResponse] = Field(..., description="List of topics matching criteria.")
    total: int = Field(..., description="Total count of topics available.")
