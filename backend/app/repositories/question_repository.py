from typing import List, Optional, Any
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.question import Question
from app.models.topic import Topic
from app.common.enums import DifficultyLevel


class QuestionRepository(BaseRepository[Question]):
    """
    Repository class providing specialized database operations for the Question model.
    """

    def __init__(self):
        super().__init__(Question)

    def get_by_topic(self, db: Session, topic_id: UUID) -> List[Question]:
        """
        Fetch all questions under a specific topic.
        """
        stmt = select(Question).where(Question.topic_id == topic_id)
        return list(db.scalars(stmt).all())

    def get_active_questions(self, db: Session) -> List[Question]:
        """
        Fetch all active questions.
        """
        stmt = select(Question).where(Question.is_active == True)
        return list(db.scalars(stmt).all())

    def search(self, db: Session, query_text: str) -> List[Question]:
        """
        Search for questions matching a substring text, case-insensitively.
        """
        stmt = select(Question).where(
            Question.question_text.ilike(f"%{query_text}%"),
            Question.is_active == True
        )
        return list(db.scalars(stmt).all())

    def get_filtered(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        subject_id: Optional[UUID] = None,
        topic_id: Optional[UUID] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        search: Optional[str] = None,
        order_by: Optional[Any] = None,
    ) -> List[Question]:
        """
        Fetch questions matching optional subject, topic, difficulty, and search filters.
        """
        stmt = select(Question)

        if topic_id:
            stmt = stmt.where(Question.topic_id == topic_id)
        elif subject_id:
            # Join topic to filter by subject
            stmt = stmt.join(Question.topic).where(Topic.subject_id == subject_id)

        if difficulty_level:
            stmt = stmt.where(Question.difficulty_level == difficulty_level)

        if search:
            stmt = stmt.where(Question.question_text.ilike(f"%{search}%"))

        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(Question.created_at.desc())

        stmt = stmt.offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    def count_filtered(
        self,
        db: Session,
        *,
        subject_id: Optional[UUID] = None,
        topic_id: Optional[UUID] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        search: Optional[str] = None,
    ) -> int:
        """
        Count total questions matching optional filters.
        """
        stmt = select(func.count()).select_from(Question)

        if topic_id:
            stmt = stmt.where(Question.topic_id == topic_id)
        elif subject_id:
            stmt = stmt.join(Question.topic).where(Topic.subject_id == subject_id)

        if difficulty_level:
            stmt = stmt.where(Question.difficulty_level == difficulty_level)

        if search:
            stmt = stmt.where(Question.question_text.ilike(f"%{search}%"))

        return db.scalar(stmt) or 0


question_repository = QuestionRepository()
