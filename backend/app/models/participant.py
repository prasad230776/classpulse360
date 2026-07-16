import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Integer, BigInteger, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from app.common.enums import ParticipantStatus

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user import User
    from app.models.response import Response


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[ParticipantStatus] = mapped_column(
        Enum(ParticipantStatus, name="participant_status"),
        default=ParticipantStatus.JOINED,
        server_default=text("'JOINED'"),
        nullable=False,
    )
    score: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        default=Decimal("0.00"),
        server_default=text("0"),
        nullable=False,
    )
    correct_answers: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    wrong_answers: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    unanswered_questions: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    total_time_ms: Mapped[int] = mapped_column(BigInteger, default=0, server_default=text("0"), nullable=False)
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=text("now()"),
        nullable=False,
    )

    # Unique constraints
    __table_args__ = (
        UniqueConstraint("session_id", "user_id", name="uq_participant_session"),
    )

    # Relationships
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="participants",
        lazy="selectin",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="participants",
        lazy="selectin",
    )
    responses: Mapped[List["Response"]] = relationship(
        "Response",
        back_populates="participant",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Participant(id={self.id}, session_id={self.session_id}, user_id={self.user_id}, score={self.score})>"
