from sqlalchemy.orm import Session
from scripts.helpers import logger

from app.common.enums import UserRole
from app.schemas.session import SessionCreate
from app.services.session_service import session_service
from app.services.participant_service import participant_service
from app.repositories.session_repository import session_repository


def seed_sessions(db: Session, quizzes: list, users: dict) -> list:
    """
    Seed session rooms, participant logs, and response submissions.
    """
    logger.info("Seeding Sessions and Participant Activity...")
    teacher = users.get(UserRole.TEACHER)
    teacher_id = teacher.id if teacher else None

    student = users.get(UserRole.STUDENT)
    student_id = student.id if student else None

    seeded = []
    if not teacher_id or not quizzes:
        return seeded

    quiz = quizzes[0]

    # Check if a session already exists for this quiz and teacher
    existing = (
        db.query(session_repository.model)
        .filter(
            session_repository.model.quiz_id == quiz.id,
            session_repository.model.created_by == teacher_id,
        )
        .first()
    )

    if not existing:
        obj_in = SessionCreate(
            quiz_id=quiz.id, created_by=teacher_id, delivery_mode="INTERACTIVE"
        )
        session = session_service.create_session(db, obj_in=obj_in)
        logger.info(
            f"Created Session: Room Code {session.room_code} for Quiz {quiz.title}"
        )

        # Start the session
        session = session_service.start_session(db, session_id=session.id)
        logger.info("Session status moved to LIVE.")

        # Seed Student Participant joining
        if student_id:
            participant = participant_service.join_session(
                db, session_id=session.id, user_id=student_id
            )
            logger.info(
                f"Studentast joined session. Participant ID: {participant.id}"
            )

            # Seed a sample response if quiz questions exist
            quiz_obj = quiz
            if quiz_obj.quiz_questions:
                first_qq = quiz_obj.quiz_questions[0]
                # Set active question in transient cache
                session_service.activate_question(
                    db, session_id=session.id, question_id=first_qq.question_id
                )
                logger.info(f"Active question set to: {first_qq.question_id}")

                resp = participant_service.submit_answer(
                    db,
                    participant_id=participant.id,
                    question_id=first_qq.question_id,
                    selected_answer={"id": "a"},
                    response_time_ms=1200,
                )
                logger.info(
                    f"Seeded student answer response. Correct: {resp.is_correct}"
                )

        seeded.append(session)
    else:
        logger.info(
            f"Session room code {existing.room_code} already exists, skipping."
        )
        seeded.append(existing)

    return seeded
