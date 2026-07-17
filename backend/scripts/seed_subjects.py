from sqlalchemy.orm import Session
from scripts.helpers import logger, fake

from app.schemas.subject import SubjectCreate
from app.services.subject_service import subject_service
from app.repositories.subject_repository import subject_repository


def seed_subjects(db: Session) -> dict:
    """
    Seed core subjects.
    """
    logger.info("Seeding Subjects...")
    subject_data = [
        {"name": "Mathematics Core", "code": "MATH101"},
        {"name": "Physics Core", "code": "PHYS101"},
    ]
    seeded = {}
    for subj_info in subject_data:
        existing = subject_repository.get_by_code(db, code=subj_info["code"])
        if not existing:
            obj_in = SubjectCreate(
                name=subj_info["name"],
                code=subj_info["code"],
                description=fake.sentence(),
            )
            subject = subject_service.create_subject(db, obj_in=obj_in)
            logger.info(f"Created Subject: {subject.name} ({subject.code})")
            seeded[subject.code] = subject
        else:
            logger.info(f"Subject {subj_info['code']} already exists, skipping.")
            seeded[subj_info["code"]] = existing
    return seeded
