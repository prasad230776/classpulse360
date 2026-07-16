from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.question import Question


class QuestionRepository(BaseRepository[Question]):
    """
    Repository class providing specialized database operations for the Question model.
    """

    def __init__(self):
        super().__init__(Question)

    def get_by_topic(self, db: Session, topic_id: UUID) -> List[Question]:
        """
        Fetch all questions under a specific topic.

        :param db: The active database Session.
        :param topic_id: The UUID of the parent topic.
        :return: A list of Question instances.
        """
        stmt = select(Question).where(Question.topic_id == topic_id)
        return list(db.scalars(stmt).all())

    def get_active_questions(self, db: Session) -> List[Question]:
        """
        Fetch all active questions.

        :param db: The active database Session.
        :return: A list of active Question instances.
        """
        stmt = select(Question).where(Question.is_active == True)
        return list(db.scalars(stmt).all())

    def search(self, db: Session, query_text: str) -> List[Question]:
        """
        Search for questions matching a substring text, case-insensitively.

        :param db: The active database Session.
        :param query_text: Search query substring.
        :return: A list of matching active Question instances.
        """
        stmt = select(Question).where(
            Question.question_text.ilike(f"%{query_text}%"),
            Question.is_active == True
        )
        return list(db.scalars(stmt).all())


question_repository = QuestionRepository()
