from sqlalchemy.orm import Session
from scripts.helpers import logger, fake

from app.schemas.topic import TopicCreate
from app.services.topic_service import topic_service
from app.repositories.topic_repository import topic_repository


def seed_topics(db: Session, subjects: dict) -> dict:
    """
    Seed topics under parent subjects.
    """
    logger.info("Seeding Topics...")
    topics_data = {
        "MATH101": [
            {"name": "Algebra", "code": "ALG"},
            {"name": "Calculus", "code": "CALC"},
        ],
        "PHYS101": [
            {"name": "Newtonian Mechanics", "code": "MEC"},
            {"name": "Thermodynamics", "code": "THERMO"},
        ],
    }
    seeded = {}
    for subj_code, topics_list in topics_data.items():
        subject = subjects.get(subj_code)
        if not subject:
            logger.warning(
                f"Parent subject code {subj_code} not found, skipping child topics."
            )
            continue
        for topic_info in topics_list:
            existing = topic_repository.get_by_code(
                db, subject_id=subject.id, code=topic_info["code"]
            )
            if not existing:
                obj_in = TopicCreate(
                    subject_id=subject.id,
                    name=topic_info["name"],
                    code=topic_info["code"],
                    description=fake.sentence(),
                )
                topic = topic_service.create_topic(db, obj_in=obj_in)
                logger.info(f"  Created Topic: {topic.name} ({topic.code})")
                seeded[topic_info["code"]] = topic
            else:
                logger.info(f"  Topic {topic_info['code']} already exists, skipping.")
                seeded[topic_info["code"]] = existing
    return seeded
