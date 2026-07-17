from fastapi import APIRouter, Depends, Query, status, Body
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List

from app.api.responses import APIResponse
from app.api.pagination import PaginationParams, PaginatedResponse, PageMetadata
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse
from app.services.question_service import question_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.common.enums import DifficultyLevel
from app.utils.pagination import get_page_params, get_paginated_metadata

question_router = APIRouter()

bulk_import_body_example = [
    {
        "topic_id": "ce4b4d7d-b437-4cc6-95db-bd2b53f1248b",
        "created_by": "1a717870-3364-4286-97b8-af854d817a3f",
        "question_text": "What is the capital of France?",
        "question_type": "MCQ_SINGLE",
        "options": {
            "choices": [
                {"id": "a", "text": "London"},
                {"id": "b", "text": "Paris"},
                {"id": "c", "text": "Rome"}
            ]
        },
        "correct_answer": {"id": "b"},
        "difficulty_level": "EASY",
        "default_marks": "1.00",
        "default_time_limit_seconds": 30
    }
]


@question_router.get(
    "/",
    response_model=PaginatedResponse[QuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="List and filter questions",
)
def list_questions(
    pagination: PaginationParams = Depends(),
    subject_id: Optional[UUID] = Query(None, description="Filter by parent Subject UUID"),
    topic_id: Optional[UUID] = Query(None, description="Filter by parent Topic UUID"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    search: Optional[str] = Query(None, description="Search keyword for question text"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sorting direction"),
    db: Session = Depends(get_db),
):
    """
    Retrieve questions from the bank supporting dynamic paging, keyword searches,
    and filtering by subject, topic, or difficulty level.
    """
    offset, limit = get_page_params(pagination.page, pagination.size)
    results = question_service.list_questions_filtered(
        db,
        offset=offset,
        limit=limit,
        subject_id=subject_id,
        topic_id=topic_id,
        difficulty_level=difficulty,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    total = question_service.count_questions_filtered(
        db,
        subject_id=subject_id,
        topic_id=topic_id,
        difficulty_level=difficulty,
        search=search,
    )
    metadata = get_paginated_metadata(total, pagination.page, pagination.size)

    return PaginatedResponse(
        success=True,
        message="Questions list retrieved successfully.",
        data=[QuestionResponse.model_validate(q) for q in results],
        metadata=PageMetadata(**metadata),
    )


@question_router.get(
    "/{id}",
    response_model=APIResponse[QuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get question by ID",
)
def get_question(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve profile details for a specific question by UUID.
    """
    q = question_service.get_question(db, question_id=id)
    return APIResponse(
        success=True,
        message="Question retrieved successfully.",
        data=QuestionResponse.model_validate(q),
    )


@question_router.post(
    "/",
    response_model=APIResponse[QuestionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new question",
)
def create_question(
    obj_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Add a new question template to the question bank.
    """
    q = question_service.create_question(db, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Question created successfully.",
        data=QuestionResponse.model_validate(q),
    )


@question_router.put(
    "/{id}",
    response_model=APIResponse[QuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="Update question details",
)
def update_question(
    id: UUID,
    obj_in: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Modify configuration parameters for an existing question.
    """
    q = question_service.update_question(db, question_id=id, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Question details updated successfully.",
        data=QuestionResponse.model_validate(q),
    )


@question_router.delete(
    "/{id}",
    response_model=APIResponse[QuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete a question",
)
def delete_question(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Remove a question template from the bank.
    """
    q = question_service.delete_question(db, question_id=id)
    return APIResponse(
        success=True,
        message="Question deleted successfully.",
        data=QuestionResponse.model_validate(q),
    )


@question_router.post(
    "/bulk",
    response_model=APIResponse[List[QuestionResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Bulk import questions",
)
def bulk_import_questions(
    obj_in_list: List[QuestionCreate] = Body(
        ..., examples=[bulk_import_body_example]
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Import multiple questions in bulk inside a single transactional database commit.
    """
    questions = question_service.create_questions_bulk(db, obj_in_list=obj_in_list)
    return APIResponse(
        success=True,
        message=f"Successfully imported {len(questions)} questions.",
        data=[QuestionResponse.model_validate(q) for q in questions],
    )
