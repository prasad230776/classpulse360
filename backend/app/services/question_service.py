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

from app.common.enums import DifficultyLevel

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

    def list_questions_filtered(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        subject_id: Optional[UUID] = None,
        topic_id: Optional[UUID] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ) -> List[Question]:
        """
        List questions matching optional filters and custom sorting.
        """
        order_attr = None
        if sort_by:
            if hasattr(Question, sort_by):
                order_attr = getattr(Question, sort_by)
                if sort_order.lower() == "desc":
                    order_attr = order_attr.desc()
                else:
                    order_attr = order_attr.asc()

        return question_repository.get_filtered(
            db,
            offset=offset,
            limit=limit,
            subject_id=subject_id,
            topic_id=topic_id,
            difficulty_level=difficulty_level,
            search=search,
            order_by=order_attr,
        )

    def count_questions_filtered(
        self,
        db: Session,
        *,
        subject_id: Optional[UUID] = None,
        topic_id: Optional[UUID] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        search: Optional[str] = None,
    ) -> int:
        """
        Count total questions matching filters.
        """
        return question_repository.count_filtered(
            db,
            subject_id=subject_id,
            topic_id=topic_id,
            difficulty_level=difficulty_level,
            search=search,
        )

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

    def create_questions_bulk(
        self, db: Session, *, obj_in_list: List[QuestionCreate]
    ) -> List[Question]:
        """
        Import multiple questions in a single transactional database commit.
        """
        logger.info(f"Bulk importing {len(obj_in_list)} questions.")
        db_objs = []
        for obj_in in obj_in_list:
            if not topic_repository.exists(db, obj_in.topic_id):
                raise ResourceNotFoundException("Topic", obj_in.topic_id)
            if not user_repository.exists(db, obj_in.created_by):
                raise ResourceNotFoundException("User (Creator)", obj_in.created_by)
            if obj_in.question_type.value.startswith("MCQ") and not obj_in.options:
                raise MCQOptionsInvalidException("MCQ questions must include choices options.")

            obj_data = obj_in.model_dump(exclude_unset=True)
            db_obj = Question(**obj_data)
            db.add(db_obj)
            db_objs.append(db_obj)

        try:
            db.commit()
            for obj in db_objs:
                db.refresh(obj)
        except Exception:
            db.rollback()
            raise
        return db_objs

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
