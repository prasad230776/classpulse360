import pytest
from sqlalchemy.orm import Session
from app.repositories.subject_repository import subject_repository
from app.repositories.topic_repository import topic_repository
from app.schemas.subject import SubjectCreate
from app.schemas.topic import TopicCreate


def test_create_and_get_topics(db: Session):
    """
    Test creating topics and fetching them by subject.
    """
    # Parent Subject
    subj_in = SubjectCreate(name="Test Mathematics", code="TESTMATH01")
    subject = subject_repository.create(db, obj_in=subj_in)

    topic_in1 = TopicCreate(subject_id=subject.id, name="Algebra", code="ALG01")
    topic_in2 = TopicCreate(subject_id=subject.id, name="Calculus", code="CALC01")

    topic_repository.create(db, obj_in=topic_in1)
    topic_repository.create(db, obj_in=topic_in2)

    topics = topic_repository.get_by_subject(db, subject.id)
    assert len(topics) == 2
    assert any(t.code == "ALG01" for t in topics)

    fetched_topic = topic_repository.get_by_code(db, subject.id, "CALC01")
    assert fetched_topic is not None
    assert fetched_topic.name == "Calculus"
