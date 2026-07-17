from typing import Optional, List, Any
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

    def get_filtered(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        order_by: Optional[Any] = None,
    ) -> List[Institution]:
        """
        Fetch institutions filtered by search keyword and active state.
        """
        stmt = select(Institution)
        if is_active is not None:
            stmt = stmt.where(Institution.is_active == is_active)
        if search:
            stmt = stmt.where(
                (Institution.name.ilike(f"%{search}%"))
                | (Institution.code.ilike(f"%{search}%"))
            )
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(Institution.created_at.desc())

        stmt = stmt.offset(offset).limit(limit)
        return list(db.scalars(stmt).all())

    def count_filtered(
        self,
        db: Session,
        *,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """
        Count institutions matching search and active state filters.
        """
        stmt = select(func.count()).select_from(Institution)
        if is_active is not None:
            stmt = stmt.where(Institution.is_active == is_active)
        if search:
            stmt = stmt.where(
                (Institution.name.ilike(f"%{search}%"))
                | (Institution.code.ilike(f"%{search}%"))
            )
        return db.scalar(stmt) or 0


institution_repository = InstitutionRepository()
