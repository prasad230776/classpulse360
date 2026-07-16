from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.session import Session as QuizSession
from app.common.enums import SessionStatus


class SessionRepository(BaseRepository[QuizSession]):
    """
    Repository class providing specialized database operations for the live Session model.
    """

    def __init__(self):
        super().__init__(QuizSession)

    def get_by_room_code(self, db: Session, room_code: str) -> Optional[QuizSession]:
        """
        Fetch a live session by its unique alphanumeric room code.

        :param db: The active database Session.
        :param room_code: Alphanumeric code (e.g. 6-digit room pin).
        :return: The matching Session, or None.
        """
        stmt = select(QuizSession).where(QuizSession.room_code == room_code)
        return db.scalars(stmt).first()

    def get_active_sessions(self, db: Session) -> List[QuizSession]:
        """
        Fetch all active sessions currently in LIVE or PAUSED execution status.

        :param db: The active database Session.
        :return: A list of active Session records.
        """
        stmt = select(QuizSession).where(
            QuizSession.status.in_([SessionStatus.LIVE, SessionStatus.PAUSED]),
            QuizSession.is_active == True
        )
        return list(db.scalars(stmt).all())


session_repository = SessionRepository()
