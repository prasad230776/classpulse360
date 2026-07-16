from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.institution import Institution


class InstitutionRepository(BaseRepository[Institution]):
    """
    Repository class providing specialized database operations for the Institution model.
    """

    def __init__(self):
        super().__init__(Institution)

    def get_by_code(self, db: Session, code: str) -> Optional[Institution]:
        """
        Fetch a single institution by its unique code.

        :param db: The active database Session.
        :param code: The unique string code.
        :return: The matching Institution, or None.
        """
        stmt = select(Institution).where(Institution.code == code)
        return db.scalars(stmt).first()

    def code_exists(self, db: Session, code: str) -> bool:
        """
        Check if an institution code is already taken.

        :param db: The active database Session.
        :param code: The unique string code.
        :return: True if the code exists, otherwise False.
        """
        stmt = select(func.count()).select_from(Institution).where(Institution.code == code)
        return db.scalar(stmt) > 0


institution_repository = InstitutionRepository()
