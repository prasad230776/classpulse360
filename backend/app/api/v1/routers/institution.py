from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from app.api.responses import APIResponse
from app.api.pagination import PaginationParams, PaginatedResponse, PageMetadata
from app.schemas.institution import InstitutionCreate, InstitutionUpdate, InstitutionResponse
from app.services.institution_service import institution_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import require_role
from app.common.enums import UserRole
from app.utils.pagination import get_page_params, get_paginated_metadata

institution_router = APIRouter()


@institution_router.get(
    "/",
    response_model=PaginatedResponse[InstitutionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all institutions",
)
def list_institutions(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search keyword for name or code"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sorting direction"),
    db: Session = Depends(get_db),
):
    """
    Retrieve registered institutions supporting dynamic paging, keyword searches, and custom sorting.
    """
    offset, limit = get_page_params(pagination.page, pagination.size)
    results = institution_service.list_institutions(
        db,
        offset=offset,
        limit=limit,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total = institution_service.count_institutions(db, search=search, is_active=is_active)
    metadata = get_paginated_metadata(total, pagination.page, pagination.size)

    return PaginatedResponse(
        success=True,
        message="Institutions list retrieved successfully.",
        data=[InstitutionResponse.model_validate(r) for r in results],
        metadata=PageMetadata(**metadata),
    )


@institution_router.get(
    "/{id}",
    response_model=APIResponse[InstitutionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get institution by ID",
)
def get_institution(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve profile details for a specific institution by UUID.
    """
    inst = institution_service.get_institution(db, institution_id=id)
    return APIResponse(
        success=True,
        message="Institution retrieved successfully.",
        data=InstitutionResponse.model_validate(inst),
    )


@institution_router.post(
    "/",
    response_model=APIResponse[InstitutionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new institution",
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_institution(
    obj_in: InstitutionCreate, db: Session = Depends(get_db)
):
    """
    Register a new institution (restricted to administrators).
    """
    inst = institution_service.create_institution(db, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Institution created successfully.",
        data=InstitutionResponse.model_validate(inst),
    )


@institution_router.put(
    "/{id}",
    response_model=APIResponse[InstitutionResponse],
    status_code=status.HTTP_200_OK,
    summary="Update institution details",
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def update_institution(
    id: UUID, obj_in: InstitutionUpdate, db: Session = Depends(get_db)
):
    """
    Modify configuration parameters for an existing institution (restricted to administrators).
    """
    inst = institution_service.update_institution(db, institution_id=id, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Institution details updated successfully.",
        data=InstitutionResponse.model_validate(inst),
    )


@institution_router.delete(
    "/{id}",
    response_model=APIResponse[InstitutionResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete an institution",
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def delete_institution(id: UUID, db: Session = Depends(get_db)):
    """
    Remove an institution profile from database persistence (restricted to administrators).
    """
    inst = institution_service.delete_institution(db, institution_id=id)
    return APIResponse(
        success=True,
        message="Institution deleted successfully.",
        data=InstitutionResponse.model_validate(inst),
    )
