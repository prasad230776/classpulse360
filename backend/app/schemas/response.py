from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class ResponseBase(BaseModel):
    """
    Base Pydantic schema representing a student's answer response to a single question.
    """
    participant_id: UUID = Field(..., description="UUID of the participant submitting this answer.")
    question_id: UUID = Field(..., description="UUID of the question being answered.")
    visited: bool = Field(False, description="Flag indicating if the student has visited this question.")
    is_marked_for_review: bool = Field(False, description="Flag indicating if the student marked it to review later.")
    selected_answer: Optional[Dict[str, Any]] = Field(None, description="JSON dictionary containing choice selection details.")
    is_correct: Optional[bool] = Field(None, description="Flag indicating response correctness accuracy.")
    score_awarded: Decimal = Field(Decimal("0.00"), ge=0, description="Actual score marks awarded for this response.")
    response_time_ms: Optional[int] = Field(None, ge=0, description="Response time in milliseconds.")
    submitted_at: Optional[datetime] = Field(None, description="Timestamp when response was sent.")


class ResponseCreate(ResponseBase):
    """
    Schema for creating a new response.
    """
    pass


class ResponseUpdate(BaseModel):
    """
    Schema for updating response values (e.g. marking correctness, changing selected choices).
    """
    visited: Optional[bool] = None
    is_marked_for_review: Optional[bool] = None
    selected_answer: Optional[Dict[str, Any]] = None
    is_correct: Optional[bool] = None
    score_awarded: Optional[Decimal] = Field(None, ge=0)
    response_time_ms: Optional[int] = Field(None, ge=0)
    submitted_at: Optional[datetime] = None


class ResponseResponse(ResponseBase):
    """
    Response schema returning complete saved response parameters.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the response record.")
    created_at: datetime = Field(..., description="Timestamp when the response record was created.")


class ResponseListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of student responses.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[ResponseResponse] = Field(..., description="List of responses matching criteria.")
    total: int = Field(..., description="Total count of responses available.")
