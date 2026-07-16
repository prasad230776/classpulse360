import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from app.common.enums import DeliveryMode, SessionStatus

if TYPE_CHECKING:
    from app.models.quiz import Quiz
    from app.models.user import User
    from app.models.participant import Participant


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    room_code: Mapped[Optional[str]] = mapped_column(String(10), unique=True, nullable=True)
    delivery_mode: Mapped[DeliveryMode] = mapped_column(
        Enum(DeliveryMode, name="delivery_mode"),
        default=DeliveryMode.INTERACTIVE,
        server_default=text("'INTERACTIVE'"),
        nullable=False,
    )
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status"),
        default=SessionStatus.DRAFT,
        server_default=text("'DRAFT'"),
        nullable=False,
    )
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
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
    quiz: Mapped["Quiz"] = relationship(
        "Quiz",
        back_populates="sessions",
        lazy="selectin",
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="sessions",
        lazy="selectin",
    )
    participants: Mapped[List["Participant"]] = relationship(
        "Participant",
        back_populates="session",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, room_code='{self.room_code}', status='{self.status}')>"
