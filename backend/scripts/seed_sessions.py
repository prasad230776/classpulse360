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

    # Find the Advanced OS Assignment Quiz from the quizzes list
    assignment_quiz = None
    for q in quizzes:
        if q.title == "Advanced OS Assignment Quiz":
            assignment_quiz = q
            break

    if assignment_quiz and teacher_id and student_id:
        existing_asg_sess = (
            db.query(session_repository.model)
            .filter(
                session_repository.model.quiz_id == assignment_quiz.id,
                session_repository.model.created_by == teacher_id,
            )
            .first()
        )
        if not existing_asg_sess:
            obj_in = SessionCreate(
                quiz_id=assignment_quiz.id,
                created_by=teacher_id,
                delivery_mode="ASSIGNMENT",
            )
            asg_session = session_service.create_session(db, obj_in=obj_in)
            asg_session = session_service.start_session(db, session_id=asg_session.id)
            
            # Student joins
            part = participant_service.join_session(db, session_id=asg_session.id, user_id=student_id)
            
            # Submit responses for questions (Advanced OS Assignment Quiz has questions associated)
            questions_list = [qq.question for qq in assignment_quiz.quiz_questions]
            if len(questions_list) >= 3:
                # 1. URL Submission (Graded)
                resp_url = participant_service.submit_answer(
                    db,
                    participant_id=part.id,
                    question_id=questions_list[0].id,
                    selected_answer={"url": "https://github.com/student/classpulse360-solution"},
                    response_time_ms=5000,
                    submission_status=SubmissionStatus.SUBMITTED,
                )
                participant_service.grade_response(
                    db,
                    participant_id=part.id,
                    question_id=questions_list[0].id,
                    score_awarded=Decimal("8.50"),
                    feedback="Good codebase structure.",
                    is_correct=True,
                )

                # 2. FILE Submission (Graded)
                resp_file = participant_service.submit_answer(
                    db,
                    participant_id=part.id,
                    question_id=questions_list[1].id,
                    selected_answer={
                        "file_name": "system_design_report.pdf",
                        "storage_path": f"{part.id}/{questions_list[1].id}/system_design_report.pdf",
                        "mime_type": "application/pdf",
                        "size": 256000,
                    },
                    response_time_ms=8000,
                    submission_status=SubmissionStatus.SUBMITTED,
                )
                participant_service.grade_response(
                    db,
                    participant_id=part.id,
                    question_id=questions_list[1].id,
                    score_awarded=Decimal("18.00"),
                    feedback="Excellent architectural diagram and explanation.",
                    is_correct=True,
                )

                # 3. TEXT Submission (Ungraded)
                participant_service.submit_answer(
                    db,
                    participant_id=part.id,
                    question_id=questions_list[2].id,
                    selected_answer={"text": "A process has states: New, Ready, Running, Waiting, Terminated."},
                    response_time_ms=12000,
                    submission_status=SubmissionStatus.SUBMITTED,
                )
            logger.info("Seeded Advanced OS Assignment Quiz session, submissions (URL, FILE, TEXT) and grades.")
            seeded.append(asg_session)
        else:
            seeded.append(existing_asg_sess)

    return seeded
