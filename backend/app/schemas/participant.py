from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import ParticipantStatus


class ParticipantBase(BaseModel):
    """
    Base Pydantic schema for a Participant entry, representing a student's session state.
    """
    session_id: UUID = Field(..., description="UUID of the joined session.")
    user_id: UUID = Field(..., description="UUID of the student user.")
    status: ParticipantStatus = Field(ParticipantStatus.JOINED, description="State of student activity inside the room.")
    score: Decimal = Field(Decimal("0.00"), ge=0, description="Total aggregated score achieved by the participant.")
    correct_answers: int = Field(0, ge=0, description="Total count of accurately answered questions.")
    wrong_answers: int = Field(0, ge=0, description="Total count of incorrectly answered questions.")
    unanswered_questions: int = Field(0, ge=0, description="Total count of skipped or timed-out questions.")
    total_time_ms: int = Field(0, ge=0, description="Aggregated response duration time in milliseconds.")
    rank: Optional[int] = Field(None, description="Calculated leaderboard position rank.")
    joined_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the student joined the room.")
    submitted_at: Optional[datetime] = Field(None, description="Timestamp when the student submitted their test/session.")


class ParticipantCreate(BaseModel):
    """
    Schema for adding a new student user to an active room session.
    """
    session_id: UUID = Field(..., description="UUID of the room session to join.")
    user_id: UUID = Field(..., description="UUID of the student joining.")
    status: Optional[ParticipantStatus] = Field(ParticipantStatus.JOINED, description="Initial participant status.")


class ParticipantUpdate(BaseModel):
    """
    Schema for updating a participant's score metrics, time metrics, or status.
    """
    status: Optional[ParticipantStatus] = None
    score: Optional[Decimal] = Field(None, ge=0)
    correct_answers: Optional[int] = Field(None, ge=0)
    wrong_answers: Optional[int] = Field(None, ge=0)
    unanswered_questions: Optional[int] = Field(None, ge=0)
    total_time_ms: Optional[int] = Field(None, ge=0)
    rank: Optional[int] = None
    submitted_at: Optional[datetime] = None


class ParticipantResponse(ParticipantBase):
    """
    Response schema returning participant status metrics.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the participant entry.")
    created_at: datetime = Field(..., description="Timestamp when the participant joined.")


class ParticipantListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of participants (useful for live leaderboards).
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[ParticipantResponse] = Field(..., description="List of participants matching criteria.")
    total: int = Field(..., description="Total count of participants available.")
