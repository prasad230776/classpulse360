import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.repositories.subject_repository import subject_repository
from app.exceptions import ResourceNotFoundException, ResourceAlreadyExistsException

logger = logging.getLogger(__name__)


class SubjectService:
    """
    Business service layer managing Subjects.
    """

    def get_subject(self, db: Session, subject_id: UUID) -> Subject:
        """
        Fetch a subject by UUID.
        """
        subj = subject_repository.get_by_id(db, subject_id)
        if not subj:
            raise ResourceNotFoundException("Subject", subject_id)
        return subj

    def get_subject_by_code(self, db: Session, code: str) -> Subject:
        """
        Fetch a subject by code.
        """
        subj = subject_repository.get_by_code(db, code)
        if not subj:
            raise ResourceNotFoundException("Subject", code)
        return subj

    def list_subjects(self, db: Session, *, offset: int = 0, limit: int = 100) -> List[Subject]:
        """
        List subjects.
        """
        return subject_repository.get_all(db, offset=offset, limit=limit)

    def count_subjects(self, db: Session) -> int:
        """
        Count total subjects.
        """
        return subject_repository.count(db)

    def create_subject(self, db: Session, *, obj_in: SubjectCreate) -> Subject:
        """
        Create a new subject, verifying code uniqueness.
        """
        if obj_in.code and subject_repository.get_by_code(db, obj_in.code):
            raise ResourceAlreadyExistsException("Subject", "code", obj_in.code)

        logger.info(f"Creating subject: {obj_in.name}")
        return subject_repository.create(db, obj_in=obj_in)

    def update_subject(self, db: Session, *, subject_id: UUID, obj_in: SubjectUpdate) -> Subject:
        """
        Update subject details.
        """
        db_obj = self.get_subject(db, subject_id)

        if obj_in.code and obj_in.code != db_obj.code:
            if subject_repository.get_by_code(db, obj_in.code):
                raise ResourceAlreadyExistsException("Subject", "code", obj_in.code)

        logger.info(f"Updating subject: {subject_id}")
        return subject_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_subject(self, db: Session, *, subject_id: UUID) -> Subject:
        """
        Delete a subject.
        """
        self.get_subject(db, subject_id)
        logger.info(f"Deleting subject: {subject_id}")
        return subject_repository.delete(db, id=subject_id)


subject_service = SubjectService()
