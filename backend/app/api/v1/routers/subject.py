from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from app.api.responses import APIResponse
from app.api.pagination import PaginationParams, PaginatedResponse, PageMetadata
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.services.subject_service import subject_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import require_role
from app.common.enums import UserRole
from app.utils.pagination import get_page_params, get_paginated_metadata

subject_router = APIRouter()


@subject_router.get(
    "/",
    response_model=PaginatedResponse[SubjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List all subjects",
)
def list_subjects(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    """
    Retrieve registered subjects supporting dynamic paging.
    """
    offset, limit = get_page_params(pagination.page, pagination.size)
    results = subject_service.list_subjects(db, offset=offset, limit=limit)
    total = subject_service.count_subjects(db)
    metadata = get_paginated_metadata(total, pagination.page, pagination.size)

    return PaginatedResponse(
        success=True,
        message="Subjects list retrieved successfully.",
        data=[SubjectResponse.model_validate(s) for s in results],
        metadata=PageMetadata(**metadata),
    )


@subject_router.get(
    "/{id}",
    response_model=APIResponse[SubjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Get subject by ID",
)
def get_subject(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve profile details for a specific subject by UUID.
    """
    subj = subject_service.get_subject(db, subject_id=id)
    return APIResponse(
        success=True,
        message="Subject retrieved successfully.",
        data=SubjectResponse.model_validate(subj),
    )


@subject_router.post(
    "/",
    response_model=APIResponse[SubjectResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new subject",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))],
)
def create_subject(obj_in: SubjectCreate, db: Session = Depends(get_db)):
    """
    Register a new subject/course (restricted to teachers and administrators).
    """
    subj = subject_service.create_subject(db, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Subject created successfully.",
        data=SubjectResponse.model_validate(subj),
    )


@subject_router.put(
    "/{id}",
    response_model=APIResponse[SubjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Update subject details",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))],
)
def update_subject(
    id: UUID, obj_in: SubjectUpdate, db: Session = Depends(get_db)
):
    """
    Modify configuration parameters for an existing subject (restricted to teachers and administrators).
    """
    subj = subject_service.update_subject(db, subject_id=id, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Subject updated successfully.",
        data=SubjectResponse.model_validate(subj),
    )


@subject_router.delete(
    "/{id}",
    response_model=APIResponse[SubjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete a subject",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN))],
)
def delete_subject(id: UUID, db: Session = Depends(get_db)):
    """
    Remove a subject profile from database persistence (restricted to teachers and administrators).
    """
    subj = subject_service.delete_subject(db, subject_id=id)
    return APIResponse(
        success=True,
        message="Subject deleted successfully.",
        data=SubjectResponse.model_validate(subj),
    )
