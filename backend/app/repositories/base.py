from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository class providing default CRUD operations for a SQLAlchemy model.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize the base repository with the specified model class.

        :param model: The SQLAlchemy model class (subclass of Base).
        """
        self.model = model

    def get_by_id(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Retrieve a single record by its primary key ID.

        :param db: The active database Session.
        :param id: The primary key value to query.
        :return: The matching model instance, or None if not found.
        """
        return db.get(self.model, id)

    def get_all(
        self,
        db: Session,
        *,
        offset: int = 0,
        limit: int = 100,
        order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """
        Retrieve multiple records with support for offset, limit, and ordering.

        :param db: The active database Session.
        :param offset: The number of rows to skip.
        :param limit: The maximum number of rows to return.
        :param order_by: The model attributes to sort results by.
        :return: A list of matching model instances.
        """
        stmt = select(self.model).offset(offset).limit(limit)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        return list(db.scalars(stmt).all())

    def create(self, db: Session, *, obj_in: Any) -> ModelType:
        """
        Insert a new record into the database, handling transaction commit and rollback.

        :param db: The active database Session.
        :param obj_in: A Pydantic schema or dictionary containing creation attributes.
        :return: The newly created model instance with refreshed database defaults.
        """
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.model_dump(exclude_unset=True)

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except Exception:
            db.rollback()
            raise
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[Any, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing database record, handling transaction commit and rollback.

        :param db: The active database Session.
        :param db_obj: The existing database model instance to modify.
        :param obj_in: A Pydantic schema or dictionary containing updated attributes.
        :return: The updated model instance with refreshed database defaults.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
        except Exception:
            db.rollback()
            raise
        return db_obj

    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """
        Delete a database record by its primary key ID, handling transaction commit and rollback.

        :param db: The active database Session.
        :param id: The primary key value of the record to delete.
        :return: The deleted model instance, or None if the record was not found.
        """
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            try:
                db.commit()
            except Exception:
                db.rollback()
                raise
        return obj

    def exists(self, db: Session, id: Any) -> bool:
        """
        Check if a record exists in the table by its primary key ID.

        :param db: The active database Session.
        :param id: The primary key value to check.
        :return: True if the record exists, otherwise False.
        """
        stmt = select(func.count()).select_from(self.model).where(self.model.id == id)
        return db.scalar(stmt) > 0

    def count(self, db: Session) -> int:
        """
        Calculate the total number of records in the table.

        :param db: The active database Session.
        :return: The total row count.
        """
        stmt = select(func.count()).select_from(self.model)
        return db.scalar(stmt) or 0
