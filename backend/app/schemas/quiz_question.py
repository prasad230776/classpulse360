from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class QuizQuestionBase(BaseModel):
    """
    Base Pydantic schema for a QuizQuestion association.
    """
    quiz_id: UUID = Field(..., description="UUID of the parent quiz.")
    question_id: UUID = Field(..., description="UUID of the question being associated.")
    question_order: Optional[int] = Field(None, ge=1, description="Sort order positioning inside the quiz.")
    marks: Optional[Decimal] = Field(None, gt=0, description="Quiz-specific score weight for correct response.")
    negative_marks: Optional[Decimal] = Field(None, ge=0, description="Quiz-specific penalty weight for incorrect response.")
    time_limit_seconds: Optional[int] = Field(None, gt=0, description="Quiz-specific response timer limit.")


class QuizQuestionCreate(QuizQuestionBase):
    """
    Schema for creating a new Quiz-Question association.
    """
    pass


class QuizQuestionUpdate(BaseModel):
    """
    Schema for updating configuration parameters on an existing association.
    """
    question_order: Optional[int] = Field(None, ge=1)
    marks: Optional[Decimal] = Field(None, gt=0)
    negative_marks: Optional[Decimal] = Field(None, ge=0)
    time_limit_seconds: Optional[int] = Field(None, gt=0)


class QuizQuestionResponse(QuizQuestionBase):
    """
    Response schema returning complete configuration details for the association.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the quiz-question association.")
    created_at: datetime = Field(..., description="Timestamp when the association was registered.")


class QuizQuestionListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of quiz-question associations.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[QuizQuestionResponse] = Field(..., description="List of quiz-question associations matching criteria.")
    total: int = Field(..., description="Total count of quiz-question associations available.")
