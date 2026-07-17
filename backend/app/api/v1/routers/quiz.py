from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

from app.api.responses import APIResponse
from app.api.pagination import PaginationParams, PaginatedResponse, PageMetadata
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizResponse
from app.schemas.quiz_question import QuizQuestionResponse
from app.services.quiz_service import quiz_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import get_current_user, require_role
from app.common.enums import UserRole
from app.utils.pagination import get_page_params, get_paginated_metadata

quiz_router = APIRouter()


class QuizQuestionAssign(BaseModel):
    question_id: UUID = Field(..., description="UUID of the question to assign")
    question_order: Optional[int] = Field(None, ge=1, description="Order index in quiz")
    marks: Optional[Decimal] = Field(None, gt=0, description="Marks allocated")
    negative_marks: Optional[Decimal] = Field(None, ge=0, description="Negative marks penalty")
    time_limit_seconds: Optional[int] = Field(None, gt=0, description="Time limit for response")


@quiz_router.get(
    "/",
    response_model=PaginatedResponse[QuizResponse],
    status_code=status.HTTP_200_OK,
    summary="List all quizzes",
)
def list_quizzes(
    pagination: PaginationParams = Depends(),
    teacher_id: Optional[UUID] = Query(None, description="Filter by creator Teacher UUID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve quizzes supporting dynamic paging.
    If teacher_id is supplied, filters down to quizzes created by that teacher.
    """
    offset, limit = get_page_params(pagination.page, pagination.size)
    if teacher_id:
        results = quiz_service.list_quizzes_by_teacher(db, teacher_id=teacher_id)
        # Apply manual slicing for compatibility with existing service method
        results = results[offset : offset + limit]
        total = len(results)
    else:
        results = quiz_service.list_quizzes(db, offset=offset, limit=limit)
        total = len(quiz_service.list_quizzes(db))  # Get total count

    metadata = get_paginated_metadata(total, pagination.page, pagination.size)

    return PaginatedResponse(
        success=True,
        message="Quizzes list retrieved successfully.",
        data=[QuizResponse.model_validate(q) for q in results],
        metadata=PageMetadata(**metadata),
    )


@quiz_router.get(
    "/{id}",
    response_model=APIResponse[QuizResponse],
    status_code=status.HTTP_200_OK,
    summary="Get quiz by ID",
)
def get_quiz(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve profile details for a specific quiz template by UUID.
    """
    quiz = quiz_service.get_quiz(db, quiz_id=id)
    return APIResponse(
        success=True,
        message="Quiz retrieved successfully.",
        data=QuizResponse.model_validate(quiz),
    )


@quiz_router.post(
    "/",
    response_model=APIResponse[QuizResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quiz template",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
def create_quiz(obj_in: QuizCreate, db: Session = Depends(get_db)):
    """
    Register a new quiz template shell (restricted to teachers).
    """
    quiz = quiz_service.create_quiz(db, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Quiz created successfully.",
        data=QuizResponse.model_validate(quiz),
    )


@quiz_router.put(
    "/{id}",
    response_model=APIResponse[QuizResponse],
    status_code=status.HTTP_200_OK,
    summary="Update quiz details",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
def update_quiz(
    id: UUID, obj_in: QuizUpdate, db: Session = Depends(get_db)
):
    """
    Modify configuration parameters for an existing quiz template (restricted to teachers).
    """
    quiz = quiz_service.update_quiz(db, quiz_id=id, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Quiz updated successfully.",
        data=QuizResponse.model_validate(quiz),
    )


@quiz_router.delete(
    "/{id}",
    response_model=APIResponse[QuizResponse],
    status_code=status.HTTP_200_OK,
    summary="Delete a quiz template",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
def delete_quiz(id: UUID, db: Session = Depends(get_db)):
    """
    Remove a quiz template shell (restricted to teachers).
    """
    quiz = quiz_service.delete_quiz(db, quiz_id=id)
    return APIResponse(
        success=True,
        message="Quiz deleted successfully.",
        data=QuizResponse.model_validate(quiz),
    )


@quiz_router.post(
    "/{id}/publish",
    response_model=APIResponse[QuizResponse],
    status_code=status.HTTP_200_OK,
    summary="Publish a quiz",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
def publish_quiz(id: UUID, db: Session = Depends(get_db)):
    """
    Publishes a quiz so it can be assigned to active rooms (restricted to teachers).
    """
    quiz = quiz_service.publish_quiz(db, quiz_id=id)
    return APIResponse(
        success=True,
        message="Quiz published successfully.",
        data=QuizResponse.model_validate(quiz),
    )


@quiz_router.post(
    "/{id}/unpublish",
    response_model=APIResponse[QuizResponse],
    status_code=status.HTTP_200_OK,
    summary="Unpublish a quiz",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
def unpublish_quiz(id: UUID, db: Session = Depends(get_db)):
    """
    Unpublishes a quiz to hide it from new rooms (restricted to teachers).
    """
    quiz = quiz_service.unpublish_quiz(db, quiz_id=id)
    return APIResponse(
        success=True,
        message="Quiz unpublished successfully.",
        data=QuizResponse.model_validate(quiz),
    )


@quiz_router.post(
    "/{id}/duplicate",
    response_model=APIResponse[QuizResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate a quiz template",
)
def duplicate_quiz(
    id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.TEACHER)),
):
    """
    Creates a full duplicate copy of a quiz template along with all its mapped questions (restricted to teachers).
    """
    quiz = quiz_service.duplicate_quiz(db, quiz_id=id, created_by=current_user.id)
    return APIResponse(
        success=True,
        message="Quiz template duplicated successfully.",
        data=QuizResponse.model_validate(quiz),
    )


@quiz_router.post(
    "/{id}/questions",
    response_model=APIResponse[List[QuizQuestionResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Assign questions to quiz",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
def assign_questions(
    id: UUID,
    payload: List[QuizQuestionAssign],
    db: Session = Depends(get_db),
):
    """
    Link multiple questions to a quiz template (restricted to teachers).
    """
    results = []
    for item in payload:
        assoc = quiz_service.add_question_to_quiz(
            db,
            quiz_id=id,
            question_id=item.question_id,
            question_order=item.question_order,
            marks=item.marks,
            negative_marks=item.negative_marks,
            time_limit_seconds=item.time_limit_seconds,
        )
        results.append(QuizQuestionResponse.model_validate(assoc))

    return APIResponse(
        success=True,
        message=f"Successfully assigned {len(results)} questions to the quiz.",
        data=results,
    )


@quiz_router.delete(
    "/{id}/questions/{question_id}",
    response_model=APIResponse[QuizQuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="Remove question from quiz",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
def remove_question(
    id: UUID, question_id: UUID, db: Session = Depends(get_db)
):
    """
    Unlink a question from a quiz template (restricted to teachers).
    """
    assoc = quiz_service.remove_question_from_quiz(db, quiz_id=id, question_id=question_id)
    return APIResponse(
        success=True,
        message="Question removed from quiz successfully.",
        data=QuizQuestionResponse.model_validate(assoc),
    )
