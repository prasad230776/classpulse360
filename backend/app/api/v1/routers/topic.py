from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from app.api.responses import APIResponse
from app.api.pagination import PaginationParams, PaginatedResponse, PageMetadata
from app.schemas.topic import TopicCreate, TopicUpdate, TopicResponse
from app.services.topic_service import topic_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import require_role
from app.common.enums import UserRole
from app.utils.pagination import get_page_params, get_paginated_metadata

topic_router = APIRouter()


@topic_router.get(
    "/",
    response_model=PaginatedResponse[TopicResponse],
    status_code=status.HTTP_200_OK,
    summary="List all topics",
)
def list_topics(
    pagination: PaginationParams = Depends(),
    subject_id: Optional[UUID] = Query(None, description="Filter by parent Subject UUID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve registered topics supporting dynamic paging.
    If subject_id is supplied, filters down to topics under that subject.
    """
    offset, limit = get_page_params(pagination.page, pagination.size)
    if subject_id:
        results = topic_service.list_topics_by_subject(db, subject_id=subject_id)
        # Apply manual slicing for compatibility with existing service method
        results = results[offset : offset + limit]
        total = len(results)
    else:
        results = topic_service.list_topics(db, offset=offset, limit=limit)
        total = len(topic_service.list_topics(db))  # Get total count

    metadata = get_paginated_metadata(total, pagination.page, pagination.size)

    return PaginatedResponse(
        success=True,
        message="Topics list retrieved successfully.",
        data=[TopicResponse.model_validate(t) for t in results],
        metadata=PageMetadata(**metadata),
    )


@topic_router.get(
    "/{id}",
    response_model=APIResponse[TopicResponse],
    status_code=status.HTTP_200_OK,
    summary="Get topic by ID",
)
def get_topic(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve profile details for a specific topic by UUID.
    """
    topic = topic_service.get_topic(db, topic_id=id)
    return APIResponse(
        success=True,
        message="Topic retrieved successfully.",
        data=TopicResponse.model_validate(topic),
    )


@topic_router.post(
    "/",
    response_model=APIResponse[TopicResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new topic",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))],
)
def create_topic(obj_in: TopicCreate, db: Session = Depends(get_db)):
    """
    Register a new topic under a subject (restricted to teachers and administrators).
    """
    topic = topic_service.create_topic(db, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Topic created successfully.",
        data=TopicResponse.model_validate(topic),
    )


@topic_router.put(
    "/{id}",
    response_model=APIResponse[TopicResponse],
    status_code=status.HTTP_200_OK,
    summary="Update topic details",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))],
)
def update_topic(
    id: UUID, obj_in: TopicUpdate, db: Session = Depends(get_db)
):
    """
    Modify configuration parameters for an existing topic (restricted to teachers and administrators).
    """
    topic = topic_service.update_topic(db, topic_id=id, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Topic updated successfully.",
        data=TopicResponse.model_validate(topic),
    )


@topic_router.delete(
    "/{id}",
    response_model=APIResponse[TopicResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete a topic",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))],
)
def delete_topic(id: UUID, db: Session = Depends(get_db)):
    """
    Remove a topic profile from database persistence (restricted to teachers and administrators).
    """
    topic = topic_service.delete_topic(db, topic_id=id)
    return APIResponse(
        success=True,
        message="Topic deleted successfully.",
        data=TopicResponse.model_validate(topic),
    )
