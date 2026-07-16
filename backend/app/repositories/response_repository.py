from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.response import Response


class ResponseRepository(BaseRepository[Response]):
    """
    Repository class providing specialized database operations for the Response answer model.
    """

    def __init__(self):
        super().__init__(Response)

    def get_by_participant(self, db: Session, participant_id: UUID) -> List[Response]:
        """
        Fetch all answer responses submitted by a participant.

        :param db: The active database Session.
        :param participant_id: The UUID of the participant.
        :return: A list of Response records.
        """
        stmt = select(Response).where(Response.participant_id == participant_id)
        return list(db.scalars(stmt).all())

    def get_response(self, db: Session, participant_id: UUID, question_id: UUID) -> Optional[Response]:
        """
        Fetch a single answer response by participant ID and question ID.

        :param db: The active database Session.
        :param participant_id: The UUID of the participant.
        :param question_id: The UUID of the question.
        :return: The matching Response, or None.
        """
        stmt = select(Response).where(
            Response.participant_id == participant_id,
            Response.question_id == question_id
        )
        return db.scalars(stmt).first()


response_repository = ResponseRepository()
