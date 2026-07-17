from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import GradingStatus, SubmissionStatus


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
    feedback: Optional[str] = Field(None, description="Teacher's grading feedback.")
    grading_status: GradingStatus = Field(GradingStatus.PENDING, description="Current status of grading.")
    submission_status: SubmissionStatus = Field(SubmissionStatus.SUBMITTED, description="Submission status.")


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
    feedback: Optional[str] = None
    grading_status: Optional[GradingStatus] = None
    submission_status: Optional[SubmissionStatus] = None


class ResponseResponse(ResponseBase):
    """
    Response schema returning complete saved response parameters.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the response record.")
    created_at: datetime = Field(..., description="Timestamp when the response record was created.")

    @classmethod
    def model_validate(cls, obj: Any, *args, **kwargs):
        from app.services.storage_service import storage_service
        from copy import deepcopy
        
        if hasattr(obj, "__dict__") or (hasattr(obj, "_mapping") if hasattr(obj, "_mapping") else False):
            # It's an ORM object or Row mapping
            data = {
                "id": getattr(obj, "id"),
                "participant_id": getattr(obj, "participant_id"),
                "question_id": getattr(obj, "question_id"),
                "visited": getattr(obj, "visited", False),
                "is_marked_for_review": getattr(obj, "is_marked_for_review", False),
                "is_correct": getattr(obj, "is_correct", None),
                "score_awarded": getattr(obj, "score_awarded", Decimal("0.00")),
                "response_time_ms": getattr(obj, "response_time_ms", None),
                "submitted_at": getattr(obj, "submitted_at", None),
                "feedback": getattr(obj, "feedback", None),
                "grading_status": getattr(obj, "grading_status", None),
                "submission_status": getattr(obj, "submission_status", None),
                "created_at": getattr(obj, "created_at"),
            }
            selected_answer = deepcopy(getattr(obj, "selected_answer")) if getattr(obj, "selected_answer") else None
        elif isinstance(obj, dict):
            data = deepcopy(obj)
            selected_answer = data.get("selected_answer")
        else:
            return super().model_validate(obj, *args, **kwargs)
            
        if isinstance(selected_answer, dict) and "storage_path" in selected_answer:
            storage_path = selected_answer.get("storage_path")
            if storage_path:
                selected_answer["file_url"] = storage_service.get_signed_url(storage_path)
                
        data["selected_answer"] = selected_answer
        return cls(**data)


class ResponseListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of student responses.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[ResponseResponse] = Field(..., description="List of responses matching criteria.")
    total: int = Field(..., description="Total count of responses available.")


class ResponseGradeRequest(BaseModel):
    score_awarded: Decimal = Field(..., ge=0, description="Marks assigned for the submission.")
    feedback: Optional[str] = Field(None, description="Optional textual feedback.")
    is_correct: Optional[bool] = Field(None, description="Whether the submission is correct.")
