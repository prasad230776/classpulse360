import pytest
from sqlalchemy.orm import Session
from app.repositories.institution_repository import institution_repository
from app.schemas.institution import InstitutionCreate, InstitutionUpdate
from app.common.enums import InstitutionType


def test_create_institution(db: Session):
    """
    Test creating a new institution.
    """
    obj_in = InstitutionCreate(
        code="TEST-INST-001",
        name="Test Institution",
        institution_type=InstitutionType.COLLEGE,
        is_active=True
    )
    db_obj = institution_repository.create(db, obj_in=obj_in)
    assert db_obj.id is not None
    assert db_obj.code == "TEST-INST-001"
    assert db_obj.name == "Test Institution"


def test_get_institution_by_id(db: Session):
    """
    Test retrieving an institution by primary key.
    """
    obj_in = InstitutionCreate(
        code="TEST-INST-002",
        name="Another Test Inst",
        institution_type=InstitutionType.UNIVERSITY
    )
    db_obj = institution_repository.create(db, obj_in=obj_in)

    fetched_obj = institution_repository.get_by_id(db, db_obj.id)
    assert fetched_obj is not None
    assert fetched_obj.id == db_obj.id
    assert fetched_obj.code == "TEST-INST-002"


def test_get_by_code_and_exists(db: Session):
    """
    Test specialized code lookup and existence checks.
    """
    code = "TEST-INST-003"
    assert not institution_repository.code_exists(db, code)

    obj_in = InstitutionCreate(
        code=code,
        name="Third Test Inst",
        institution_type=InstitutionType.SCHOOL
    )
    institution_repository.create(db, obj_in=obj_in)

    assert institution_repository.code_exists(db, code)
    fetched_obj = institution_repository.get_by_code(db, code)
    assert fetched_obj is not None
    assert fetched_obj.name == "Third Test Inst"


def test_get_all_pagination_and_ordering(db: Session):
    """
    Test retrieve all pagination and sorting.
    """
    inst1 = InstitutionCreate(code="AA-INST", name="Alpha Inst", institution_type=InstitutionType.CORPORATE)
    inst2 = InstitutionCreate(code="ZZ-INST", name="Omega Inst", institution_type=InstitutionType.CORPORATE)
    institution_repository.create(db, obj_in=inst1)
    institution_repository.create(db, obj_in=inst2)

    # Test count
    total_count = institution_repository.count(db)
    assert total_count >= 2

    # Test ordering (order by code asc)
    from app.models.institution import Institution
    results = institution_repository.get_all(db, limit=100, order_by=Institution.code.asc())
    # Find indices
    codes = [r.code for r in results]
    assert "AA-INST" in codes
    assert "ZZ-INST" in codes
    assert codes.index("AA-INST") < codes.index("ZZ-INST")


def test_update_institution(db: Session):
    """
    Test updating an existing institution.
    """
    obj_in = InstitutionCreate(
        code="TEST-INST-004",
        name="Update Target",
        institution_type=InstitutionType.SCHOOL
    )
    db_obj = institution_repository.create(db, obj_in=obj_in)

    update_in = InstitutionUpdate(name="Updated Name", phone="123456")
    updated_obj = institution_repository.update(db, db_obj=db_obj, obj_in=update_in)
    assert updated_obj.name == "Updated Name"
    assert updated_obj.phone == "123456"


def test_delete_institution(db: Session):
    """
    Test deleting an institution by primary key.
    """
    obj_in = InstitutionCreate(
        code="TEST-INST-005",
        name="Delete Target",
        institution_type=InstitutionType.SCHOOL
    )
    db_obj = institution_repository.create(db, obj_in=obj_in)

    deleted_obj = institution_repository.delete(db, id=db_obj.id)
    assert deleted_obj is not None
    assert deleted_obj.id == db_obj.id

    # Verify it does not exist
    assert not institution_repository.exists(db, db_obj.id)
