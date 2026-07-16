import uuid
from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, BigInteger, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.participant import Participant
    from app.models.question import Question


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    participant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("participants.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    visited: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)
    is_marked_for_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
    )
    selected_answer: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    score_awarded: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        server_default=text("0"),
        nullable=False,
    )
    response_time_ms: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )

    # Unique constraints
    __table_args__ = (
        UniqueConstraint("participant_id", "question_id", name="uq_response"),
    )

    # Relationships
    participant: Mapped["Participant"] = relationship(
        "Participant",
        back_populates="responses",
        lazy="selectin",
    )
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="responses",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Response(id={self.id}, participant_id={self.participant_id}, question_id={self.question_id}, is_correct={self.is_correct})>"
