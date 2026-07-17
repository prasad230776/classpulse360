import logging
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.session import Session as QuizSession
from app.models.participant import Participant
from app.schemas.session import SessionCreate, SessionUpdate
from app.repositories.session_repository import session_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.user_repository import user_repository
from app.repositories.question_repository import question_repository
from app.exceptions import ResourceNotFoundException, BusinessRuleException
from app.common.enums import SessionStatus

logger = logging.getLogger(__name__)


class SessionService:
    """
    Business service layer managing active classroom room sessions.
    """

    # Transient in-memory storage of current active question IDs keyed by session ID
    _active_questions: Dict[UUID, UUID] = {}

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
        if not quiz_repository.exists(db, obj_in.quiz_id):
            raise ResourceNotFoundException("Quiz", obj_in.quiz_id)

        if not user_repository.exists(db, obj_in.created_by):
            raise ResourceNotFoundException("User (Host)", obj_in.created_by)

        logger.info(f"Launching session room for quiz {obj_in.quiz_id}")
        return session_repository.create(db, obj_in=obj_in)

    def start_session(self, db: Session, *, session_id: UUID) -> QuizSession:
        """
        Move session status to LIVE. Validates transitions.
        """
        db_obj = self.get_session(db, session_id)

        if db_obj.status == SessionStatus.LIVE:
            return db_obj

        if db_obj.status == SessionStatus.COMPLETED:
            raise BusinessRuleException("Cannot start a completed session.", code="INVALID_TRANSITION")

        update_in = SessionUpdate(
            status=SessionStatus.LIVE,
            started_at=datetime.utcnow()
        )

        logger.info(f"Starting session room {session_id} LIVE")
        return session_repository.update(db, db_obj=db_obj, obj_in=update_in)

    def pause_session(self, db: Session, *, session_id: UUID) -> QuizSession:
        """
        Move session status from LIVE to PAUSED.
        """
        db_obj = self.get_session(db, session_id)

        if db_obj.status == SessionStatus.PAUSED:
            return db_obj

        if db_obj.status != SessionStatus.LIVE:
            raise BusinessRuleException(
                f"Cannot pause session in {db_obj.status.value} state.", code="INVALID_TRANSITION"
            )

        update_in = SessionUpdate(status=SessionStatus.PAUSED)
        logger.info(f"Pausing session room {session_id}")
        return session_repository.update(db, db_obj=db_obj, obj_in=update_in)

    def resume_session(self, db: Session, *, session_id: UUID) -> QuizSession:
        """
        Move session status from PAUSED to LIVE.
        """
        db_obj = self.get_session(db, session_id)

        if db_obj.status == SessionStatus.LIVE:
            return db_obj

        if db_obj.status != SessionStatus.PAUSED:
            raise BusinessRuleException(
                f"Cannot resume session in {db_obj.status.value} state.", code="INVALID_TRANSITION"
            )

        update_in = SessionUpdate(status=SessionStatus.LIVE)
        logger.info(f"Resuming session room {session_id}")
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

    def activate_question(self, db: Session, *, session_id: UUID, question_id: UUID) -> UUID:
        """
        Explicitly sets the currently active question for the session.
        """
        sess = self.get_session(db, session_id)
        # Verify question is linked to this session's quiz
        linked_question_ids = [qq.question_id for qq in sess.quiz.quiz_questions]
        if question_id not in linked_question_ids:
            raise BusinessRuleException(
                f"Question {question_id} is not linked to this session's quiz.",
                code="UNLINKED_QUESTION"
            )

        self._active_questions[session_id] = question_id
        logger.info(f"Activated question {question_id} on session {session_id}")
        return question_id

    def get_active_question(self, db: Session, *, session_id: UUID) -> Optional[UUID]:
        """
        Retrieves the currently active question ID. Defaults to the first question if unset.
        """
        if session_id in self._active_questions:
            return self._active_questions[session_id]

        # Default fallback to first question of the quiz
        sess = self.get_session(db, session_id)
        ordered_qqs = sorted(sess.quiz.quiz_questions, key=lambda x: x.question_order or 0)
        if ordered_qqs:
            first_q_id = ordered_qqs[0].question_id
            self._active_questions[session_id] = first_q_id
            return first_q_id

        return None

    def next_question(self, db: Session, *, session_id: UUID) -> Optional[UUID]:
        """
        Advances the session's active question pointer to the next quiz question in order.
        """
        sess = self.get_session(db, session_id)
        ordered_qqs = sorted(sess.quiz.quiz_questions, key=lambda x: x.question_order or 0)
        if not ordered_qqs:
            raise BusinessRuleException("Quiz does not contain any questions.", code="EMPTY_QUIZ")

        curr_q = self.get_active_question(db, session_id=session_id)
        if not curr_q:
            next_q = ordered_qqs[0].question_id
        else:
            # Find current index
            curr_idx = -1
            for i, qq in enumerate(ordered_qqs):
                if qq.question_id == curr_q:
                    curr_idx = i
                    break

            if curr_idx == -1 or curr_idx == len(ordered_qqs) - 1:
                # Wrap around or stay on last question
                next_q = ordered_qqs[0].question_id
            else:
                next_q = ordered_qqs[curr_idx + 1].question_id

        self._active_questions[session_id] = next_q
        logger.info(f"Advanced session {session_id} to question {next_q}")
        return next_q

    def get_leaderboard(self, db: Session, *, session_id: UUID) -> List[Participant]:
        """
        Fetches participant leaderboard data sorted by score desc, then total response time.
        """
        # Ensure session exists
        self.get_session(db, session_id)
        return (
            db.query(Participant)
            .filter(Participant.session_id == session_id)
            .order_by(Participant.score.desc(), Participant.total_time_ms.asc())
            .all()
        )

    def get_participants(self, db: Session, *, session_id: UUID) -> List[Participant]:
        """
        Fetches the complete roster of participants currently registered in the session.
        """
        self.get_session(db, session_id)
        return (
            db.query(Participant)
            .filter(Participant.session_id == session_id)
            .all()
        )

    def get_session_questions(self, db: Session, *, session_id: UUID):
        """
        Retrieves all questions associated with the quiz of a session.
        """
        sess = self.get_session(db, session_id)
        ordered_qqs = sorted(sess.quiz.quiz_questions, key=lambda x: x.question_order or 0)
        return [qq.question for qq in ordered_qqs]


session_service = SessionService()
