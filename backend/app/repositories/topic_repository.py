from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.topic import Topic


class TopicRepository(BaseRepository[Topic]):
    """
    Repository class providing specialized database operations for the Topic model.
    """

    def __init__(self):
        super().__init__(Topic)

    def get_by_subject(self, db: Session, subject_id: UUID) -> List[Topic]:
        """
        Fetch all topics under a specific subject.

        :param db: The active database Session.
        :param subject_id: The UUID of the parent subject.
        :return: A list of Topic instances.
        """
        stmt = select(Topic).where(Topic.subject_id == subject_id)
        return list(db.scalars(stmt).all())

    def get_by_code(self, db: Session, subject_id: UUID, code: str) -> Optional[Topic]:
        """
        Fetch a topic by its parent subject and unique topic code.

        :param db: The active database Session.
        :param subject_id: The UUID of the parent subject.
        :param code: The code identifier of the topic.
        :return: The matching Topic, or None.
        """
        stmt = select(Topic).where(Topic.subject_id == subject_id, Topic.code == code)
        return db.scalars(stmt).first()


topic_repository = TopicRepository()
