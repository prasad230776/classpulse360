import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.institution import Institution
from app.schemas.institution import InstitutionCreate, InstitutionUpdate
from app.repositories.institution_repository import institution_repository
from app.exceptions import ResourceNotFoundException, ResourceAlreadyExistsException

logger = logging.getLogger(__name__)


class InstitutionService:
    """
    Business service layer managing Institution operations.
    """

    def get_institution(self, db: Session, institution_id: UUID) -> Institution:
        """
        Fetch an institution by its UUID.
        """
        inst = institution_repository.get_by_id(db, institution_id)
        if not inst:
            raise ResourceNotFoundException("Institution", institution_id)
        return inst

    def get_institution_by_code(self, db: Session, code: str) -> Institution:
        """
        Fetch an institution by its unique code.
        """
        inst = institution_repository.get_by_code(db, code)
        if not inst:
            raise ResourceNotFoundException("Institution", code)
        return inst

    def list_institutions(self, db: Session, *, offset: int = 0, limit: int = 100) -> List[Institution]:
        """
        List institutions with offset and limit pagination.
        """
        return institution_repository.get_all(db, offset=offset, limit=limit)

    def count_institutions(self, db: Session) -> int:
        """
        Count total institutions registered.
        """
        return institution_repository.count(db)

    def create_institution(self, db: Session, *, obj_in: InstitutionCreate) -> Institution:
        """
        Create a new institution, verifying code uniqueness.
        """
        if institution_repository.code_exists(db, obj_in.code):
            logger.warning(f"Registration attempt failed: Institution code '{obj_in.code}' already exists.")
            raise ResourceAlreadyExistsException("Institution", "code", obj_in.code)

        logger.info(f"Registering new institution: {obj_in.name} ({obj_in.code})")
        return institution_repository.create(db, obj_in=obj_in)

    def update_institution(self, db: Session, *, institution_id: UUID, obj_in: InstitutionUpdate) -> Institution:
        """
        Update institution details.
        """
        db_obj = self.get_institution(db, institution_id)

        # If updating code, check uniqueness
        if obj_in.code and obj_in.code != db_obj.code:
            if institution_repository.code_exists(db, obj_in.code):
                raise ResourceAlreadyExistsException("Institution", "code", obj_in.code)

        logger.info(f"Updating institution {institution_id}")
        return institution_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_institution(self, db: Session, *, institution_id: UUID) -> Institution:
        """
        Delete an institution.
        """
        db_obj = self.get_institution(db, institution_id)
        logger.info(f"Deleting institution {institution_id} ({db_obj.name})")
        return institution_repository.delete(db, id=institution_id)


institution_service = InstitutionService()
