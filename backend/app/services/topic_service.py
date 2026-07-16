import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicUpdate
from app.repositories.topic_repository import topic_repository
from app.repositories.subject_repository import subject_repository
from app.exceptions import ResourceNotFoundException, ResourceAlreadyExistsException

logger = logging.getLogger(__name__)


class TopicService:
    """
    Business service layer managing Topics within Subjects.
    """

    def get_topic(self, db: Session, topic_id: UUID) -> Topic:
        """
        Fetch a topic by UUID.
        """
        topic = topic_repository.get_by_id(db, topic_id)
        if not topic:
            raise ResourceNotFoundException("Topic", topic_id)
        return topic

    def list_topics(self, db: Session, *, offset: int = 0, limit: int = 100) -> List[Topic]:
        """
        List all topics.
        """
        return topic_repository.get_all(db, offset=offset, limit=limit)

    def list_topics_by_subject(self, db: Session, *, subject_id: UUID) -> List[Topic]:
        """
        List all topics under a specific subject.
        """
        if not subject_repository.exists(db, subject_id):
            raise ResourceNotFoundException("Subject", subject_id)
        return topic_repository.get_by_subject(db, subject_id)

    def create_topic(self, db: Session, *, obj_in: TopicCreate) -> Topic:
        """
        Create a new topic under a subject, verifying unique constraints.
        """
        # Validate parent subject exists
        if not subject_repository.exists(db, obj_in.subject_id):
            raise ResourceNotFoundException("Subject", obj_in.subject_id)

        # Check unique constraint (subject_id, name)
        existing_topics = topic_repository.get_by_subject(db, obj_in.subject_id)
        if any(t.name.lower() == obj_in.name.lower() for t in existing_topics):
            raise ResourceAlreadyExistsException("Topic", "name", obj_in.name)

        # Check unique constraint (subject_id, code) if code is supplied
        if obj_in.code:
            if topic_repository.get_by_code(db, obj_in.subject_id, obj_in.code):
                raise ResourceAlreadyExistsException("Topic", "code", obj_in.code)

        logger.info(f"Creating topic '{obj_in.name}' under subject {obj_in.subject_id}")
        return topic_repository.create(db, obj_in=obj_in)

    def update_topic(self, db: Session, *, topic_id: UUID, obj_in: TopicUpdate) -> Topic:
        """
        Update a topic.
        """
        db_obj = self.get_topic(db, topic_id)

        subject_id = obj_in.subject_id or db_obj.subject_id

        # Validate username/name uniqueness on name change
        if obj_in.name and obj_in.name.lower() != db_obj.name.lower():
            existing_topics = topic_repository.get_by_subject(db, subject_id)
            if any(t.name.lower() == obj_in.name.lower() for t in existing_topics):
                raise ResourceAlreadyExistsException("Topic", "name", obj_in.name)

        # Validate code uniqueness on code change
        if obj_in.code and obj_in.code != db_obj.code:
            if topic_repository.get_by_code(db, subject_id, obj_in.code):
                raise ResourceAlreadyExistsException("Topic", "code", obj_in.code)

        logger.info(f"Updating topic: {topic_id}")
        return topic_repository.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete_topic(self, db: Session, *, topic_id: UUID) -> Topic:
        """
        Delete a topic.
        """
        self.get_topic(db, topic_id)
        logger.info(f"Deleting topic: {topic_id}")
        return topic_repository.delete(db, id=topic_id)


topic_service = TopicService()
