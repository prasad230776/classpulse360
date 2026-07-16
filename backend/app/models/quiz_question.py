import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.question import Question


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    question_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    marks: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    negative_marks: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    time_limit_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )

    # Unique constraints
    __table_args__ = (
        UniqueConstraint("quiz_id", "question_id", name="uq_quiz_question"),
        UniqueConstraint("quiz_id", "question_order", name="uq_quiz_question_order"),
    )

    # Relationships
    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="quiz_questions",
        lazy="selectin",
    )
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="quiz_associations",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<QuizQuestion(id={self.id}, quiz_id={self.quiz_id}, question_id={self.question_id}, order={self.question_order})>"
