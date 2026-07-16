import logging
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.session import Session as QuizSession
from app.schemas.session import SessionCreate, SessionUpdate
from app.repositories.session_repository import session_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.user_repository import user_repository
from app.exceptions import ResourceNotFoundException
from app.common.enums import SessionStatus

logger = logging.getLogger(__name__)


class SessionService:
    """
    Business service layer managing active classroom room sessions.
    """

    def get_session(self, db: Session, session_id: UUID) -> QuizSession:
        """
        Fetch a session by UUID.
        """
        sess = session_repository.get_by_id(db, session_id)
        if not sess:
            raise ResourceNotFoundException("Session", session_id)
        return sess

    def get_session_by_room_code(self, db: Session, room_code: str) -> QuizSession:
        """
        Fetch a session by room code.
        """
        sess = session_repository.get_by_room_code(db, room_code)
        if not sess:
            raise ResourceNotFoundException("Session Room", room_code)
        return sess

    def list_sessions(self, db: Session, *, offset: int = 0, limit: int = 100) -> List[QuizSession]:
        """
        List all sessions.
        """
        return session_repository.get_all(db, offset=offset, limit=limit)

    def create_session(self, db: Session, *, obj_in: SessionCreate) -> QuizSession:
        """
        Launch a new session. Room code is generated via Postgres trigger.
        """
        # Validate quiz exists
        if not quiz_repository.exists(db, obj_in.quiz_id):
            raise ResourceNotFoundException("Quiz", obj_in.quiz_id)

        # Validate host exists
        if not user_repository.exists(db, obj_in.created_by):
            raise ResourceNotFoundException("User (Host)", obj_in.created_by)

        logger.info(f"Launching session room for quiz {obj_in.quiz_id}")
        return session_repository.create(db, obj_in=obj_in)

    def start_session(self, db: Session, *, session_id: UUID) -> QuizSession:
        """
        Move session status to LIVE and set start timestamp.
        """
        db_obj = self.get_session(db, session_id)

        if db_obj.status == SessionStatus.LIVE:
            return db_obj

        update_in = SessionUpdate(
            status=SessionStatus.LIVE,
            started_at=datetime.utcnow()
        )

        logger.info(f"Starting session room {session_id} LIVE")
        return session_repository.update(db, db_obj=db_obj, obj_in=update_in)

    def end_session(self, db: Session, *, session_id: UUID) -> QuizSession:
        """
        Complete a session, setting status to COMPLETED and recording ended timestamp.
        """
        db_obj = self.get_session(db, session_id)

        if db_obj.status == SessionStatus.COMPLETED:
            return db_obj

        update_in = SessionUpdate(
            status=SessionStatus.COMPLETED,
            ended_at=datetime.utcnow()
        )

        logger.info(f"Completing session room {session_id}")
        return session_repository.update(db, db_obj=db_obj, obj_in=update_in)


session_service = SessionService()
