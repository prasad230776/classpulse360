import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.repositories.question_repository import question_repository
from app.repositories.topic_repository import topic_repository
from app.repositories.user_repository import user_repository
from app.exceptions import ResourceNotFoundException, MCQOptionsInvalidException

logger = logging.getLogger(__name__)


class QuestionService:
    """
    Business service layer managing the Question Bank.
    """

    def get_question(self, db: Session, question_id: UUID) -> Question:
        """
        Fetch a question by UUID.
        """
        q = question_repository.get_by_id(db, question_id)
        if not q:
            raise ResourceNotFoundException("Question", question_id)
        return q

    def list_questions(self, db: Session, *, offset: int = 0, limit: int = 100) -> List[Question]:
        """
        List all questions in the bank.
        """
        return question_repository.get_all(db, offset=offset, limit=limit)

    def list_questions_by_topic(self, db: Session, *, topic_id: UUID) -> List[Question]:
        """
        List all questions associated with a specific topic.
        """
        if not topic_repository.exists(db, topic_id):
            raise ResourceNotFoundException("Topic", topic_id)
        return question_repository.get_by_topic(db, topic_id)

    def search_questions(self, db: Session, *, query: str) -> List[Question]:
        """
        Search questions containing string query text.
        """
        if not query.strip():
            return []
        return question_repository.search(db, query)

    def create_question(self, db: Session, *, obj_in: QuestionCreate) -> Question:
        """
        Create a new question. Validates parent topic and creator exist.
        """
        # Validate parent topic
        if not topic_repository.exists(db, obj_in.topic_id):
            raise ResourceNotFoundException("Topic", obj_in.topic_id)

        # Validate creator user
        if not user_repository.exists(db, obj_in.created_by):
            raise ResourceNotFoundException("User (Creator)", obj_in.created_by)

        # Simple check for MCQ questions to ensure options are supplied
        if obj_in.question_type.value.startswith("MCQ") and not obj_in.options:
            raise MCQOptionsInvalidException("MCQ questions must include a choices option structure.")

        logger.info(f"Adding new question to bank by creator {obj_in.created_by}")
        return question_repository.create(db, obj_in=obj_in)

    def update_question(self, db: Session, *, question_id: UUID, obj_in: QuestionUpdate) -> Question:
        """
        Update a question's content or configuration.
        """
        db_obj = self.get_question(db, question_id)

        # Validate topic if changing
        if obj_in.topic_id and obj_in.topic_id != db_obj.topic_id:
            if not topic_repository.exists(db, obj_in.topic_id):
                raise ResourceNotFoundException("Topic", obj_in.topic_id)

        logger.info(f"Updating question: {question_id}")
        return question_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_question(self, db: Session, *, question_id: UUID) -> Question:
        """
        Delete a question.
        """
        self.get_question(db, question_id)
        logger.info(f"Deleting question: {question_id}")
        return question_repository.delete(db, id=question_id)


# Instantiate question service
question_service = QuestionService()
