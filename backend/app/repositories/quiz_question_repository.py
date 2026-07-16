from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.quiz_question import QuizQuestion


class QuizQuestionRepository(BaseRepository[QuizQuestion]):
    """
    Repository class providing specialized database operations for the QuizQuestion association model.
    """

    def __init__(self):
        super().__init__(QuizQuestion)

    def get_questions_by_quiz_id(self, db: Session, quiz_id: UUID) -> List[QuizQuestion]:
        """
        Fetch all quiz-question associations for a specific quiz, sorted by order.

        :param db: The active database Session.
        :param quiz_id: The UUID of the quiz.
        :return: A list of QuizQuestion associations.
        """
        stmt = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id).order_by(QuizQuestion.question_order.asc())
        return list(db.scalars(stmt).all())

    def get_association(self, db: Session, quiz_id: UUID, question_id: UUID) -> Optional[QuizQuestion]:
        """
        Fetch a specific association by quiz ID and question ID.

        :param db: The active database Session.
        :param quiz_id: The UUID of the quiz.
        :param question_id: The UUID of the question.
        :return: The matching QuizQuestion, or None.
        """
        stmt = select(QuizQuestion).where(
            QuizQuestion.quiz_id == quiz_id,
            QuizQuestion.question_id == question_id
        )
        return db.scalars(stmt).first()


quiz_question_repository = QuizQuestionRepository()
