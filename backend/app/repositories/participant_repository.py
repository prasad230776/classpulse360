from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.participant import Participant


class ParticipantRepository(BaseRepository[Participant]):
    """
    Repository class providing specialized database operations for the Participant state model.
    """

    def __init__(self):
        super().__init__(Participant)

    def get_by_session(self, db: Session, session_id: UUID) -> List[Participant]:
        """
        Fetch all participants registered in a session, ordered by score descending (leaderboard view).

        :param db: The active database Session.
        :param session_id: The UUID of the session.
        :return: A list of Participant records.
        """
        stmt = select(Participant).where(Participant.session_id == session_id).order_by(Participant.score.desc())
        return list(db.scalars(stmt).all())

    def get_participant(self, db: Session, session_id: UUID, user_id: UUID) -> Optional[Participant]:
        """
        Fetch a specific participant entry by session ID and user ID.

        :param db: The active database Session.
        :param session_id: The UUID of the session.
        :param user_id: The UUID of the student user.
        :return: The matching Participant, or None.
        """
        stmt = select(Participant).where(
            Participant.session_id == session_id,
            Participant.user_id == user_id
        )
        return db.scalars(stmt).first()


participant_repository = ParticipantRepository()
