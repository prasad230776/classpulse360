import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.base import Base
from app.common.enums import VisibilityType, QuestionType, DifficultyLevel

if TYPE_CHECKING:
    from app.models.topic import Topic
    from app.models.user import User
    from app.models.quiz_question import QuizQuestion
    from app.models.response import Response


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    visibility: Mapped[VisibilityType] = mapped_column(
        Enum(VisibilityType, name="visibility_type"),
        default=VisibilityType.PRIVATE,
        server_default=text("'PRIVATE'"),
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(
        Enum(QuestionType, name="question_type"),
        default=QuestionType.MCQ_SINGLE,
        server_default=text("'MCQ_SINGLE'"),
        nullable=False,
    )
    options: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    correct_answer: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(nullable=True)
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level"),
        default=DifficultyLevel.MEDIUM,
        server_default=text("'MEDIUM'"),
        nullable=False,
    )
    default_marks: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("1.00"),
        server_default=text("1"),
        nullable=False,
    )
    default_time_limit_seconds: Mapped[int] = mapped_column(
        Integer,
        default=30,
        server_default=text("30"),
        nullable=False,
    )
    tags: Mapped[Optional[List[str]]] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )

    # Relationships
    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="questions",
        lazy="selectin",
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="questions",
        lazy="selectin",
    )
    quiz_associations: Mapped[List["QuizQuestion"]] = relationship(
        "QuizQuestion",
        back_populates="question",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    responses: Mapped[List["Response"]] = relationship(
        "Response",
        back_populates="question",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, topic_id={self.topic_id}, type='{self.question_type}', difficulty='{self.difficulty_level}')>"
