from sqlalchemy.orm import Session
from scripts.helpers import logger, fake

from app.common.enums import InstitutionType
from app.schemas.institution import InstitutionCreate
from app.services.institution_service import institution_service
from app.repositories.institution_repository import institution_repository


def seed_institutions(db: Session) -> list:
    """
    Seed sample institutions idempotently.
    """
    logger.info("Seeding Institutions...")
    institutions_data = [
        {
            "name": "ClassPulse University",
            "code": "CPU01",
            "institution_type": InstitutionType.UNIVERSITY,
        },
        {
            "name": "ClassPulse High School",
            "code": "CPH01",
            "institution_type": InstitutionType.SCHOOL,
        },
    ]
    seeded = []
    for inst in institutions_data:
        existing = institution_repository.get_by_code(db, code=inst["code"])
        if not existing:
            obj_in = InstitutionCreate(
                name=inst["name"],
                code=inst["code"],
                institution_type=inst["institution_type"],
                email=fake.company_email(),
                phone=fake.phone_number()[:20],
                website=fake.url(),
            )
            new_inst = institution_service.create_institution(db, obj_in=obj_in)
            logger.info(f"Created Institution: {new_inst.name} ({new_inst.code})")
            seeded.append(new_inst)
        else:
            logger.info(f"Institution {inst['code']} already exists, skipping.")
            seeded.append(existing)
    return seeded
