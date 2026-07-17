import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.base import Base
from app.common.enums import VisibilityType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.quiz_question import QuizQuestion
    from app.models.session import Session


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(nullable=True)
    visibility: Mapped[VisibilityType] = mapped_column(
        Enum(VisibilityType, name="visibility_type"),
        default=VisibilityType.PRIVATE,
        server_default=text("'PRIVATE'"),
        nullable=False,
    )
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)
    shuffle_options: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)
    allow_answer_change: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"), nullable=False)
    show_results_after_each_question: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )
    settings_config: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        default=dict,
        server_default=text("'{}'::jsonb"),
        nullable=True,
    )
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
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="quizzes",
        lazy="selectin",
    )
    quiz_questions: Mapped[List["QuizQuestion"]] = relationship(
        "QuizQuestion",
        back_populates="quiz",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[List["Session"]] = relationship(
        "Session",
        back_populates="quiz",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Quiz(id={self.id}, title='{self.title}', created_by={self.created_by})>"
