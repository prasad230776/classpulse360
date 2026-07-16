from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.subject import Subject


class SubjectRepository(BaseRepository[Subject]):
    """
    Repository class providing specialized database operations for the Subject model.
    """

    def __init__(self):
        super().__init__(Subject)

    def get_by_code(self, db: Session, code: str) -> Optional[Subject]:
        """
        Fetch a single subject by its unique code.

        :param db: The active database Session.
        :param code: The unique subject identifier code.
        :return: The matching Subject, or None.
        """
        stmt = select(Subject).where(Subject.code == code)
        return db.scalars(stmt).first()

    def get_active_subjects(self, db: Session) -> List[Subject]:
        """
        Fetch all active subjects.

        :param db: The active database Session.
        :return: A list of active Subject instances.
        """
        stmt = select(Subject).where(Subject.is_active == True)
        return list(db.scalars(stmt).all())


subject_repository = SubjectRepository()
