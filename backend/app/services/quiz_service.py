import logging
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.schemas.quiz import QuizCreate, QuizUpdate
from app.schemas.quiz_question import QuizQuestionCreate
from app.repositories.quiz_repository import quiz_repository
from app.repositories.user_repository import user_repository
from app.repositories.question_repository import question_repository
from app.repositories.quiz_question_repository import quiz_question_repository
from app.exceptions import ResourceNotFoundException, ResourceAlreadyExistsException, ValidationException

logger = logging.getLogger(__name__)


class QuizService:
    """
    Business service layer managing Quiz templates and question compilation.
    """

    def get_quiz(self, db: Session, quiz_id: UUID) -> Quiz:
        """
        Fetch a quiz template by UUID.
        """
        quiz = quiz_repository.get_by_id(db, quiz_id)
        if not quiz:
            raise ResourceNotFoundException("Quiz", quiz_id)
        return quiz

    def list_quizzes(self, db: Session, *, offset: int = 0, limit: int = 100) -> List[Quiz]:
        """
        List all quizzes.
        """
        return quiz_repository.get_all(db, offset=offset, limit=limit)

    def list_quizzes_by_teacher(self, db: Session, *, teacher_id: UUID) -> List[Quiz]:
        """
        List quizzes created by a specific teacher.
        """
        if not user_repository.exists(db, teacher_id):
            raise ResourceNotFoundException("User (Teacher)", teacher_id)
        return quiz_repository.get_by_teacher(db, teacher_id)

    def create_quiz(self, db: Session, *, obj_in: QuizCreate) -> Quiz:
        """
        Create a new quiz template shell.
        """
        if not user_repository.exists(db, obj_in.created_by):
            raise ResourceNotFoundException("User (Creator)", obj_in.created_by)

        logger.info(f"Creating new quiz template '{obj_in.title}' by teacher {obj_in.created_by}")
        return quiz_repository.create(db, obj_in=obj_in)

    def update_quiz(self, db: Session, *, quiz_id: UUID, obj_in: QuizUpdate) -> Quiz:
        """
        Update quiz template configurations.
        """
        db_obj = self.get_quiz(db, quiz_id)
        logger.info(f"Updating quiz template {quiz_id}")
        return quiz_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_quiz(self, db: Session, *, quiz_id: UUID) -> Quiz:
        """
        Delete a quiz template.
        """
        self.get_quiz(db, quiz_id)
        logger.info(f"Deleting quiz template {quiz_id}")
        return quiz_repository.delete(db, id=quiz_id)

    # Question Compilation Operations
    def add_question_to_quiz(
        self,
        db: Session,
        *,
        quiz_id: UUID,
        question_id: UUID,
        question_order: Optional[int] = None,
        marks: Optional[Decimal] = None,
        negative_marks: Optional[Decimal] = None,
        time_limit_seconds: Optional[int] = None
    ) -> QuizQuestion:
        """
        Link a question to a quiz, verifying constraints.
        """
        # Validate parent quiz exists
        if not quiz_repository.exists(db, quiz_id):
            raise ResourceNotFoundException("Quiz", quiz_id)

        # Validate question exists
        question = question_repository.get_by_id(db, question_id)
        if not question:
            raise ResourceNotFoundException("Question", question_id)

        # Check if already linked
        if quiz_question_repository.get_association(db, quiz_id, question_id):
            raise ResourceAlreadyExistsException("QuizQuestion", "question_id", question_id)

        # Build association payload
        assoc_in = QuizQuestionCreate(
            quiz_id=quiz_id,
            question_id=question_id,
            question_order=question_order,
            marks=marks or question.default_marks,
            negative_marks=negative_marks or Decimal("0.00"),
            time_limit_seconds=time_limit_seconds or question.default_time_limit_seconds
        )

        logger.info(f"Linking question {question_id} to quiz {quiz_id}")
        return quiz_question_repository.create(db, obj_in=assoc_in)

    def remove_question_from_quiz(self, db: Session, *, quiz_id: UUID, question_id: UUID) -> QuizQuestion:
        """
        Unlink a question from a quiz.
        """
        assoc = quiz_question_repository.get_association(db, quiz_id, question_id)
        if not assoc:
            raise ResourceNotFoundException("QuizQuestion link", f"quiz:{quiz_id}-question:{question_id}")

        logger.info(f"Unlinking question {question_id} from quiz {quiz_id}")
        return quiz_question_repository.delete(db, id=assoc.id)


quiz_service = QuizService()
