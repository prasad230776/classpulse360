from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field

from app.api.responses import APIResponse
from app.api.pagination import PaginationParams, PaginatedResponse, PageMetadata
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizResponse
from app.schemas.quiz_question import QuizQuestionResponse
from app.schemas.response import ResponseResponse, ResponseGradeRequest
from app.services.quiz_service import quiz_service
from app.services.participant_service import participant_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import get_current_user, require_role
from app.common.enums import UserRole, SubmissionStatus
from app.models.user import User
from app.models.response import Response
from app.models.participant import Participant
from app.exceptions import ResourceNotFoundException
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


@quiz_router.get(
    "/student/submissions",
    response_model=APIResponse[List[ResponseResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get logged-in student submissions",
)
def get_student_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve all submissions (responses) submitted by the logged-in student.
    """
    results = (
        db.query(Response)
        .join(Participant)
        .filter(Participant.user_id == current_user.id)
        .order_by(Response.submitted_at.desc())
        .all()
    )
    return APIResponse(
        success=True,
        message="Student submissions retrieved.",
        data=[ResponseResponse.model_validate(r) for r in results],
    )


@quiz_router.get(
    "/student/submissions/{submission_id}",
    response_model=APIResponse[ResponseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get single submission details",
)
def get_student_submission_details(
    submission_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve details for a specific submission owned by the student.
    """
    resp = (
        db.query(Response)
        .join(Participant)
        .filter(Response.id == submission_id, Participant.user_id == current_user.id)
        .first()
    )
    if not resp:
        raise ResourceNotFoundException("Submission", submission_id)
    
    return APIResponse(
        success=True,
        message="Submission details retrieved.",
        data=ResponseResponse.model_validate(resp),
    )


@quiz_router.get(
    "/{quiz_id}/submissions",
    response_model=APIResponse[List[ResponseResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get all submissions for a quiz (Teacher)",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def get_teacher_quiz_submissions(
    quiz_id: UUID,
    status: Optional[SubmissionStatus] = Query(None, description="Filter by submission status"),
    search: Optional[str] = Query(None, description="Search by student name or username"),
    db: Session = Depends(get_db),
):
    """
    Retrieve all submissions (responses) for a specific quiz with status filter and search (restricted to teachers).
    """
    from app.models.session import Session as QuizSession
    query = (
        db.query(Response)
        .join(Participant, Response.participant_id == Participant.id)
        .join(QuizSession, Participant.session_id == QuizSession.id)
        .filter(QuizSession.quiz_id == quiz_id)
    )
    
    if search:
        query = query.join(User, Participant.user_id == User.id).filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%")
            )
        )
        
    if status:
        query = query.filter(Response.submission_status == status)
        
    results = query.order_by(Response.submitted_at.desc()).all()
    return APIResponse(
        success=True,
        message="Quiz submissions retrieved.",
        data=[ResponseResponse.model_validate(r) for r in results],
    )


@quiz_router.get(
    "/{quiz_id}/submissions/{submission_id}",
    response_model=APIResponse[ResponseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get single submission details (Teacher)",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def get_teacher_submission_details(
    quiz_id: UUID,
    submission_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve details for a specific student submission under a quiz (restricted to teachers).
    """
    from app.models.session import Session as QuizSession
    resp = (
        db.query(Response)
        .join(Participant, Response.participant_id == Participant.id)
        .join(QuizSession, Participant.session_id == QuizSession.id)
        .filter(Response.id == submission_id, QuizSession.quiz_id == quiz_id)
        .first()
    )
    if not resp:
        raise ResourceNotFoundException("Submission", submission_id)
        
    return APIResponse(
        success=True,
        message="Submission details retrieved.",
        data=ResponseResponse.model_validate(resp),
    )


@quiz_router.post(
    "/{quiz_id}/submissions/{submission_id}/grade",
    response_model=APIResponse[ResponseResponse],
    status_code=status.HTTP_200_OK,
    summary="Grade a student submission (Teacher)",
    dependencies=[Depends(require_role(UserRole.TEACHER, UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def grade_quiz_submission(
    quiz_id: UUID,
    submission_id: UUID,
    payload: ResponseGradeRequest,
    db: Session = Depends(get_db),
):
    """
    Grade or update grading for a specific student submission (restricted to teachers).
    """
    from app.models.session import Session as QuizSession
    resp = (
        db.query(Response)
        .join(Participant, Response.participant_id == Participant.id)
        .join(QuizSession, Participant.session_id == QuizSession.id)
        .filter(Response.id == submission_id, QuizSession.quiz_id == quiz_id)
        .first()
    )
    if not resp:
        raise ResourceNotFoundException("Submission", submission_id)

    updated_resp = participant_service.grade_response(
        db,
        participant_id=resp.participant_id,
        question_id=resp.question_id,
        score_awarded=payload.score_awarded,
        feedback=payload.feedback,
        is_correct=payload.is_correct,
    )
    return APIResponse(
        success=True,
        message="Submission graded successfully.",
        data=ResponseResponse.model_validate(updated_resp),
    )
