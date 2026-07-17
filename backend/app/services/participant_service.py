import logging
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.participant import Participant
from app.models.response import Response
from app.schemas.participant import ParticipantCreate, ParticipantUpdate
from app.schemas.response import ResponseCreate, ResponseUpdate
from app.repositories.participant_repository import participant_repository
from app.repositories.response_repository import response_repository
from app.repositories.session_repository import session_repository
from app.repositories.user_repository import user_repository
from app.repositories.question_repository import question_repository
from app.repositories.quiz_question_repository import quiz_question_repository
from app.exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    InvalidSessionStateException,
    AnswerChangeNotAllowedException,
    BusinessRuleException,
)
from app.common.enums import ParticipantStatus, SessionStatus, SubmissionStatus

logger = logging.getLogger(__name__)


class ParticipantService:
    """
    Business service layer managing Student participation lobby and answer scoring.
    """

    def get_participant(self, db: Session, participant_id: UUID) -> Participant:
        """
        Fetch participant entry by UUID.
        """
        part = participant_repository.get_by_id(db, participant_id)
        if not part:
            raise ResourceNotFoundException("Participant", participant_id)
        return part

    def join_session(self, db: Session, *, session_id: UUID, user_id: UUID) -> Participant:
        """
        Register a student user inside a session lobby.
        """
        # Validate Session exists and is active
        session = session_repository.get_by_id(db, session_id)
        if not session or not session.is_active:
            raise ResourceNotFoundException("Active Session", session_id)

        # Validate Session is not completed
        if session.status == SessionStatus.COMPLETED:
            raise InvalidSessionStateException("Cannot join a session room that has already ended.")

        # Validate User exists
        if not user_repository.exists(db, user_id):
            raise ResourceNotFoundException("User", user_id)

        # Return existing participant if already joined
        existing = participant_repository.get_participant(db, session_id, user_id)
        if existing:
            return existing

        # Create lobby association
        logger.info(f"User {user_id} joining session room {session_id}")
        assoc_in = ParticipantCreate(session_id=session_id, user_id=user_id, status=ParticipantStatus.JOINED)
        return participant_repository.create(db, obj_in=assoc_in)

    def submit_answer(
        self,
        db: Session,
        *,
        participant_id: UUID,
        question_id: UUID,
        selected_answer: Dict[str, Any],
        response_time_ms: Optional[int] = None,
        submission_status: Optional[SubmissionStatus] = None
    ) -> Response:
        """
        Track and score student answer responses, updating participant total scores.
        """
        participant = self.get_participant(db, participant_id)
        session = session_repository.get_by_id(db, participant.session_id)
        if not session or session.status == SessionStatus.COMPLETED:
            raise InvalidSessionStateException("Cannot submit answers to a completed session.")

        question = question_repository.get_by_id(db, question_id)
        if not question:
            raise ResourceNotFoundException("Question", question_id)

        # Retrieve custom quiz-specific marks configurations (or default to base question marks)
        quiz_assoc = quiz_question_repository.get_association(db, session.quiz_id, question_id)
        if not quiz_assoc:
            raise BusinessRuleException(
                f"Question {question_id} is not associated with this session's quiz.",
                code="UNLINKED_QUESTION"
            )
        marks = quiz_assoc.marks if (quiz_assoc and quiz_assoc.marks is not None) else question.default_marks
        negative_marks = quiz_assoc.negative_marks if (quiz_assoc and quiz_assoc.negative_marks is not None) else Decimal("0.00")

        # Validate assignment submission types
        from app.common.enums import QuestionType
        if question.question_type in (QuestionType.URL, QuestionType.FILE, QuestionType.TEXT):
            if not isinstance(selected_answer, dict):
                raise BusinessRuleException("Selected answer must be a JSON dictionary.", code="INVALID_SUBMISSION")
            
            if question.question_type == QuestionType.URL:
                url = selected_answer.get("url")
                if not url or not (url.startswith("http://") or url.startswith("https://")):
                    raise BusinessRuleException("A valid URL starting with http:// or https:// is required.", code="INVALID_SUBMISSION")
            elif question.question_type == QuestionType.FILE:
                file_url = selected_answer.get("file_url")
                storage_path = selected_answer.get("storage_path")
                if not file_url and not storage_path:
                    raise BusinessRuleException("A valid file URL or storage path is required.", code="INVALID_SUBMISSION")
                if file_url and not (file_url.startswith("http://") or file_url.startswith("https://")):
                    raise BusinessRuleException("A valid file URL is required.", code="INVALID_SUBMISSION")
            elif question.question_type == QuestionType.TEXT:
                text_val = selected_answer.get("text")
                if not text_val or not isinstance(text_val, str) or len(text_val.strip()) == 0:
                    raise BusinessRuleException("Text content is required.", code="INVALID_SUBMISSION")
            
            is_correct = None
            score_awarded = Decimal("0.00")
        else:
            # Verify correct answer selection matches
            is_correct = (selected_answer == question.correct_answer)
            score_awarded = marks if is_correct else -negative_marks

        if submission_status is None:
            submission_status = SubmissionStatus.SUBMITTED

        # Check if response already exists
        existing_response = response_repository.get_response(db, participant_id, question_id)
        if existing_response:
            if existing_response.submission_status in (SubmissionStatus.SUBMITTED, SubmissionStatus.GRADED):
                config = getattr(session.quiz, "settings_config", None) or {}
                allow_attempts = config.get("allow_multiple_attempts", False) or config.get("allow_resubmission", False)
                if not allow_attempts:
                    raise BusinessRuleException(
                        "Submitted assignments cannot be modified unless the quiz configuration allows resubmission.",
                        code="RESUBMISSION_DISABLED"
                    )

            # If changing answer is locked by quiz settings, reject
            if not session.quiz.allow_answer_change:
                raise AnswerChangeNotAllowedException()

            # Calculate score adjustment difference
            score_diff = score_awarded - existing_response.score_awarded

            # Calculate accuracy updates
            correct_diff = (1 if is_correct else 0) - (1 if existing_response.is_correct else 0)
            wrong_diff = (0 if is_correct else 1) - (0 if existing_response.is_correct else 1)

            # Update Response
            update_in = ResponseUpdate(
                selected_answer=selected_answer,
                is_correct=is_correct,
                score_awarded=score_awarded,
                response_time_ms=response_time_ms,
                submitted_at=datetime.utcnow(),
                submission_status=submission_status
            )
            resp = response_repository.update(db, db_obj=existing_response, obj_in=update_in)

            # Update Participant aggregates
            part_update = ParticipantUpdate(
                score=max(Decimal("0.00"), participant.score + score_diff),
                correct_answers=max(0, participant.correct_answers + correct_diff),
                wrong_answers=max(0, participant.wrong_answers + wrong_diff),
                total_time_ms=participant.total_time_ms + (response_time_ms or 0)
            )
            participant_repository.update(db, db_obj=participant, obj_in=part_update)
            return resp

        # Create new Response
        resp_in = ResponseCreate(
            participant_id=participant_id,
            question_id=question_id,
            visited=True,
            selected_answer=selected_answer,
            is_correct=is_correct,
            score_awarded=score_awarded,
            response_time_ms=response_time_ms,
            submitted_at=datetime.utcnow(),
            submission_status=submission_status
        )
        resp = response_repository.create(db, obj_in=resp_in)

        # Update Participant aggregates
        part_update = ParticipantUpdate(
            score=max(Decimal("0.00"), participant.score + score_awarded),
            correct_answers=participant.correct_answers + (1 if is_correct else 0),
            wrong_answers=participant.wrong_answers + (0 if is_correct else 1),
            total_time_ms=participant.total_time_ms + (response_time_ms or 0)
        )
        participant_repository.update(db, db_obj=participant, obj_in=part_update)

        return resp

    def get_leaderboard(self, db: Session, *, session_id: UUID) -> List[Participant]:
        """
        Fetch participants ranked by scores.
        """
        if not session_repository.exists(db, session_id):
            raise ResourceNotFoundException("Session", session_id)
        return participant_repository.get_by_session(db, session_id)

    def leave_session(self, db: Session, *, participant_id: UUID) -> Participant:
        """
        Remove a student participant registry from the live room.
        """
        part = self.get_participant(db, participant_id)
        logger.info(f"Participant {participant_id} leaving session room.")
        return participant_repository.delete(db, id=participant_id)

    def get_participant_responses(self, db: Session, *, participant_id: UUID) -> List[Response]:
        """
        Fetch responses history for a participant.
        """
        # Verifies participant exists
        self.get_participant(db, participant_id)
        return (
            db.query(Response)
            .filter(Response.participant_id == participant_id)
            .order_by(Response.submitted_at.desc())
            .all()
        )

    def grade_response(
        self,
        db: Session,
        *,
        participant_id: UUID,
        question_id: UUID,
        score_awarded: Decimal,
        feedback: Optional[str] = None,
        is_correct: Optional[bool] = None
    ) -> Response:
        """
        Grade a participant's answer response manually, updating score aggregates.
        """
        participant = self.get_participant(db, participant_id)
        resp = response_repository.get_response(db, participant_id, question_id)
        if not resp:
            raise ResourceNotFoundException("Response", f"part={participant_id}, q={question_id}")

        if resp.submission_status == SubmissionStatus.DRAFT:
            raise BusinessRuleException("Drafts cannot be graded.", code="CANNOT_GRADE_DRAFT")
        if resp.submission_status not in (SubmissionStatus.SUBMITTED, SubmissionStatus.GRADED):
            raise BusinessRuleException("Only submitted assignments can be graded.", code="CANNOT_GRADE_NON_SUBMITTED")

        score_diff = score_awarded - resp.score_awarded
        
        correct_diff = 0
        wrong_diff = 0
        if is_correct is not None:
            old_is_correct = resp.is_correct if resp.is_correct is not None else False
            new_is_correct = is_correct
            
            if old_is_correct != new_is_correct:
                if new_is_correct:
                    correct_diff = 1
                    wrong_diff = -1
                else:
                    correct_diff = -1
                    wrong_diff = 1

        from app.common.enums import GradingStatus
        
        resp.score_awarded = score_awarded
        resp.feedback = feedback
        resp.grading_status = GradingStatus.GRADED
        resp.submission_status = SubmissionStatus.GRADED
        if is_correct is not None:
            resp.is_correct = is_correct

        db.add(resp)

        part_update = ParticipantUpdate(
            score=max(Decimal("0.00"), participant.score + score_diff),
            correct_answers=max(0, participant.correct_answers + correct_diff),
            wrong_answers=max(0, participant.wrong_answers + wrong_diff),
        )
        participant_repository.update(db, db_obj=participant, obj_in=part_update)
        
        try:
            db.commit()
            db.refresh(resp)
        except Exception:
            db.rollback()
            raise

        return resp


participant_service = ParticipantService()
