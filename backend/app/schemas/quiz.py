from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.common.enums import VisibilityType


class QuizConfig(BaseModel):
    timer_duration: Optional[int] = Field(None, ge=0, description="Overall timer duration in seconds.")
    allow_multiple_attempts: bool = Field(False, description="Allow multiple attempts on the quiz.")
    show_results_immediately: bool = Field(True, description="Display results immediately after completion.")
    show_correct_answers: bool = Field(True, description="Display correct answers in results.")
    randomize_questions: bool = Field(False, description="Randomize question delivery order.")
    require_fullscreen: bool = Field(False, description="Enforce fullscreen mode on student UI.")
    allow_question_navigation: bool = Field(True, description="Allow going back and forth between questions.")
    allow_question_review: bool = Field(True, description="Allow reviewing answers before final submission.")
    assignment_due_date: Optional[datetime] = Field(None, description="Due date and time for assignments.")
    assignment_max_file_size: Optional[int] = Field(None, ge=0, description="Maximum allowed file size in bytes.")
    allowed_file_extensions: List[str] = Field(default_factory=list, description="List of allowed file extensions.")
    allowed_submission_types: List[str] = Field(default_factory=list, description="Allowed submission types.")


class QuizBase(BaseModel):
    """
    Base Pydantic schema for a Quiz template, containing common attributes.
    """
    title: str = Field(..., min_length=1, max_length=200, description="Title of the quiz.")
    description: Optional[str] = Field(None, description="Detailed description/subtext.")
    instructions: Optional[str] = Field(None, description="Student directions shown before starting.")
    visibility: VisibilityType = Field(VisibilityType.PRIVATE, description="Access visibility permissions.")
    shuffle_questions: bool = Field(False, description="Flag to shuffle question order at delivery.")
    shuffle_options: bool = Field(False, description="Flag to shuffle option choice order at delivery.")
    allow_answer_change: bool = Field(True, description="Flag to permit students to adjust choice selections.")
    show_results_after_each_question: bool = Field(
        True,
        description="Flag to display accuracy metrics immediately after choice submission."
    )
    is_active: bool = Field(True, description="Flag indicating if the quiz is active.")
    settings_config: Optional[QuizConfig] = Field(default_factory=QuizConfig, description="Configuration settings.")


class QuizCreate(QuizBase):
    """
    Schema for creating a new Quiz. Specifies creator metadata.
    """
    created_by: UUID = Field(..., description="UUID of the creator.")


class QuizUpdate(BaseModel):
    """
    Schema for updating an existing Quiz. All fields are optional.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    instructions: Optional[str] = None
    visibility: Optional[VisibilityType] = None
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    allow_answer_change: Optional[bool] = None
    show_results_after_each_question: Optional[bool] = None
    is_active: Optional[bool] = None
    settings_config: Optional[QuizConfig] = None


class QuizResponse(QuizBase):
    """
    Response schema returning complete Quiz details, including metadata metrics.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique database UUID of the quiz.")
    created_by: UUID = Field(..., description="UUID of the creator.")
    created_at: datetime = Field(..., description="Timestamp when the quiz was drafted.")
    updated_at: datetime = Field(..., description="Timestamp when the quiz was last modified.")


class QuizListResponse(BaseModel):
    """
    Paginated API wrapper returning a count and a list of quizzes.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[QuizResponse] = Field(..., description="List of quizzes matching criteria.")
    total: int = Field(..., description="Total count of quizzes available.")
