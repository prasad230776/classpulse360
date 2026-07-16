import pytest
from sqlalchemy.orm import Session
from app.repositories.subject_repository import subject_repository
from app.schemas.subject import SubjectCreate


def test_create_and_get_subject(db: Session):
    """
    Test creating a subject and getting active ones.
    """
    subj_in = SubjectCreate(
        name="Computer Science 101",
        code="CS101",
        description="Introduction to CS",
        is_active=True
    )
    db_obj = subject_repository.create(db, obj_in=subj_in)
    assert db_obj.id is not None

    fetched = subject_repository.get_by_code(db, "CS101")
    assert fetched is not None
    assert fetched.name == "Computer Science 101"

    active_subjects = subject_repository.get_active_subjects(db)
    assert len(active_subjects) >= 1
    assert any(s.code == "CS101" for s in active_subjects)
