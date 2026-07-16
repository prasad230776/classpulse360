from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.quiz import Quiz
from app.common.enums import VisibilityType


class QuizRepository(BaseRepository[Quiz]):
    """
    Repository class providing specialized database operations for the Quiz model.
    """

    def __init__(self):
        super().__init__(Quiz)

    def get_by_teacher(self, db: Session, teacher_id: UUID) -> List[Quiz]:
        """
        Fetch all quizzes created by a specific teacher/author.

        :param db: The active database Session.
        :param teacher_id: The UUID of the teacher/author.
        :return: A list of Quiz templates.
        """
        stmt = select(Quiz).where(Quiz.created_by == teacher_id)
        return list(db.scalars(stmt).all())

    def get_published_quizzes(self, db: Session) -> List[Quiz]:
        """
        Fetch all active quizzes configured with PUBLIC or INSTITUTION visibility.

        :param db: The active database Session.
        :return: A list of published Quiz templates.
        """
        stmt = select(Quiz).where(
            Quiz.visibility.in_([VisibilityType.PUBLIC, VisibilityType.INSTITUTION]),
            Quiz.is_active == True
        )
        return list(db.scalars(stmt).all())


quiz_repository = QuizRepository()
