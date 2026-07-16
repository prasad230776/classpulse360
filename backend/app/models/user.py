import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base
from app.common.enums import UserRole, UserStatus

if TYPE_CHECKING:
    from app.models.institution import Institution
    from app.models.question import Question
    from app.models.quiz import Quiz
    from app.models.session import Session
    from app.models.participant import Participant


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    institution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.STUDENT,
        server_default=text("'STUDENT'"),
        nullable=False,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"),
        default=UserStatus.PENDING,
        server_default=text("'PENDING'"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    mobile_number: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)
    roll_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
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
    institution: Mapped[Optional["Institution"]] = relationship(
        "Institution",
        back_populates="users",
        lazy="selectin",
    )
    questions: Mapped[List["Question"]] = relationship(
        "Question",
        back_populates="creator",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    quizzes: Mapped[List["Quiz"]] = relationship(
        "Quiz",
        back_populates="creator",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    sessions: Mapped[List["Session"]] = relationship(
        "Session",
        back_populates="creator",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    participants: Mapped[List["Participant"]] = relationship(
        "Participant",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"
