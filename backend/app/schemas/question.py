from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import VisibilityType, QuestionType, DifficultyLevel


class QuestionBase(BaseModel):
    """
    Base Pydantic schema for a Question, containing core quiz content attributes.
    """
    topic_id: UUID = Field(..., description="UUID of the associated topic.")
    visibility: VisibilityType = Field(VisibilityType.PRIVATE, description="Access permissions/visibility level.")
    question_text: str = Field(..., min_length=1, description="The core text of the question (markdown supported).")
    question_type: QuestionType = Field(QuestionType.MCQ_SINGLE, description="Type/format of the question.")
    options: Dict[str, Any] = Field(
        ...,
        description="Structured JSON dictionary containing list of choice options and styling keys."
    )
    correct_answer: Dict[str, Any] = Field(
        ...,
        description="Structured JSON dictionary containing identifiers of correct choices or matches."
    )
    explanation: Optional[str] = Field(None, description="Detailed explanation/solution reference.")
    difficulty_level: DifficultyLevel = Field(DifficultyLevel.MEDIUM, description="Cognitive difficulty rating.")
    default_marks: Decimal = Field(Decimal("1.00"), gt=0, description="Standard positive score awarded for correction.")
    default_time_limit_seconds: int = Field(30, gt=0, description="Standard response timeout threshold in seconds.")
    tags: Optional[List[str]] = Field(None, description="Optional listing of metadata labels.")
    is_active: bool = Field(True, description="Flag indicating if the question is active.")


class QuestionCreate(QuestionBase):
    """
    Schema for creating a new Question. Specifies creator metadata.
    """
    created_by: UUID = Field(..., description="UUID of the creating Teacher/Admin.")


class QuestionUpdate(BaseModel):
    """
    Schema for updating an existing Question. All fields are optional.
    """
    topic_id: Optional[UUID] = None
    visibility: Optional[VisibilityType] = None
    question_text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[QuestionType] = None
    options: Optional[Dict[str, Any]] = None
    correct_answer: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    default_marks: Optional[Decimal] = Field(None, gt=0)
    default_time_limit_seconds: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class QuestionResponse(QuestionBase):
    """
    Response schema returning complete Question details, including metadata metrics.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the question.")
    created_by: UUID = Field(..., description="UUID of the creator.")
    created_at: datetime = Field(..., description="Timestamp when the question was added.")
    updated_at: datetime = Field(..., description="Timestamp when the question was last updated.")


class QuestionListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of questions.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[QuestionResponse] = Field(..., description="List of questions matching criteria.")
    total: int = Field(..., description="Total count of questions available.")
