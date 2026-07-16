from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import DeliveryMode, SessionStatus


class SessionBase(BaseModel):
    """
    Base Pydantic schema for a live interactive Quiz Session, containing common attributes.
    """
    quiz_id: UUID = Field(..., description="UUID of the quiz template used.")
    room_code: Optional[str] = Field(None, max_length=10, description="Unique alphanumeric code used to join.")
    delivery_mode: DeliveryMode = Field(DeliveryMode.INTERACTIVE, description="Classroom delivery format.")
    status: SessionStatus = Field(SessionStatus.DRAFT, description="Current execution state of the session.")
    scheduled_at: Optional[datetime] = Field(None, description="Planned future start timestamp.")
    started_at: Optional[datetime] = Field(None, description="Actual execution start timestamp.")
    ended_at: Optional[datetime] = Field(None, description="Actual completion timestamp.")
    is_active: bool = Field(True, description="Flag indicating if the session is active.")


class SessionCreate(SessionBase):
    """
    Schema for launching/scheduling a new live Session.
    """
    created_by: UUID = Field(..., description="UUID of the session host/creator (Teacher).")


class SessionUpdate(BaseModel):
    """
    Schema for updating configuration parameters or progressing status on an existing Session.
    """
    quiz_id: Optional[UUID] = None
    room_code: Optional[str] = Field(None, max_length=10)
    delivery_mode: Optional[DeliveryMode] = None
    status: Optional[SessionStatus] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class SessionResponse(SessionBase):
    """
    Response schema returning complete Session details, including current execution values.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the session.")
    created_by: UUID = Field(..., description="UUID of the creator.")
    created_at: datetime = Field(..., description="Timestamp when the session was created.")
    updated_at: datetime = Field(..., description="Timestamp when the session was last modified.")


class SessionListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of sessions.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[SessionResponse] = Field(..., description="List of sessions matching criteria.")
    total: int = Field(..., description="Total count of sessions available.")
