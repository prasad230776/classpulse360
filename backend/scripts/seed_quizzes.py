from sqlalchemy.orm import Session
from scripts.helpers import logger

from app.common.enums import UserRole
from app.schemas.quiz import QuizCreate
from app.services.quiz_service import quiz_service
from app.repositories.quiz_repository import quiz_repository


def seed_quizzes(db: Session, questions: list, users: dict) -> list:
    """
    Seed sample quiz templates.
    """
    logger.info("Seeding Quiz Templates...")
    teacher = users.get(UserRole.TEACHER)
    teacher_id = teacher.id if teacher else None

    seeded = []
    if not teacher_id:
        return seeded

    existing = (
        db.query(quiz_repository.model)
        .filter(quiz_repository.model.title == "Introductory STEM Quiz")
        .first()
    )

    if not existing:
        obj_in = QuizCreate(
            title="Introductory STEM Quiz",
            description="A quick diagnostic quiz covering algebra and basic physics forces.",
            created_by=teacher_id,
            shuffle_questions=True,
            shuffle_options=False,
            allow_answer_change=True,
            show_results_after_each_question=True,
        )
        quiz = quiz_service.create_quiz(db, obj_in=obj_in)

        # Associate questions
        for idx, q in enumerate(questions):
            quiz_service.add_question_to_quiz(
                db,
                quiz_id=quiz.id,
                question_id=q.id,
                question_order=idx + 1,
                marks=q.default_marks,
                time_limit_seconds=q.default_time_limit_seconds,
            )
        logger.info(f"Created Quiz: {quiz.title} with {len(questions)} questions.")
        seeded.append(quiz)
    else:
        logger.info(f"Quiz '{existing.title}' already exists, skipping.")
        seeded.append(existing)

    # 1. Interactive Quiz
    existing_interactive = db.query(quiz_repository.model).filter(quiz_repository.model.title == "Interactive Live Quiz").first()
    if not existing_interactive:
        obj_in = QuizCreate(
            title="Interactive Live Quiz",
            description="A real-time competitive classroom quiz.",
            created_by=teacher_id,
            shuffle_questions=False,
            shuffle_options=True,
            allow_answer_change=True,
            show_results_after_each_question=True,
            settings_config={
                "show_results_immediately": True,
                "allow_question_navigation": True,
            }
        )
        q_interactive = quiz_service.create_quiz(db, obj_in=obj_in)
        for idx, q in enumerate(questions):
            quiz_service.add_question_to_quiz(db, quiz_id=q_interactive.id, question_id=q.id, question_order=idx + 1, marks=q.default_marks)
        seeded.append(q_interactive)
    else:
        seeded.append(existing_interactive)

    # 2. Classroom Exam
    existing_exam = db.query(quiz_repository.model).filter(quiz_repository.model.title == "Classroom Semester Exam").first()
    if not existing_exam:
        obj_in = QuizCreate(
            title="Classroom Semester Exam",
            description="Proctored semester final exam.",
            created_by=teacher_id,
            shuffle_questions=True,
            shuffle_options=True,
            allow_answer_change=False,
            show_results_after_each_question=False,
            settings_config={
                "show_results_immediately": False,
                "show_correct_answers": False,
                "require_fullscreen": True,
                "allow_question_navigation": False,
            }
        )
        q_exam = quiz_service.create_quiz(db, obj_in=obj_in)
        for idx, q in enumerate(questions):
            quiz_service.add_question_to_quiz(db, quiz_id=q_exam.id, question_id=q.id, question_order=idx + 1, marks=q.default_marks)
        seeded.append(q_exam)
    else:
        seeded.append(existing_exam)

    # 3. Self Practice Quiz
    existing_practice = db.query(quiz_repository.model).filter(quiz_repository.model.title == "Self Practice Algebra Quiz").first()
    if not existing_practice:
        obj_in = QuizCreate(
            title="Self Practice Algebra Quiz",
            description="Ungraded practice quiz with multiple attempts permitted.",
            created_by=teacher_id,
            shuffle_questions=True,
            shuffle_options=True,
            allow_answer_change=True,
            show_results_after_each_question=True,
            settings_config={
                "allow_multiple_attempts": True,
                "show_results_immediately": True,
            }
        )
        q_practice = quiz_service.create_quiz(db, obj_in=obj_in)
        for idx, q in enumerate(questions):
            quiz_service.add_question_to_quiz(db, quiz_id=q_practice.id, question_id=q.id, question_order=idx + 1, marks=q.default_marks)
        seeded.append(q_practice)
    else:
        seeded.append(existing_practice)

    # 4. Assignment Quiz
    existing_assignment = db.query(quiz_repository.model).filter(quiz_repository.model.title == "Advanced OS Assignment Quiz").first()
    if not existing_assignment:
        obj_in = QuizCreate(
            title="Advanced OS Assignment Quiz",
            description="Take-home assignment quiz.",
            created_by=teacher_id,
            shuffle_questions=False,
            shuffle_options=False,
            allow_answer_change=True,
            show_results_after_each_question=False,
            settings_config={
                "allowed_submission_types": ["FILE", "URL", "TEXT"],
                "allowed_file_extensions": ["pdf", "docx"],
                "assignment_max_file_size": 10485760,
            }
        )
        q_assignment = quiz_service.create_quiz(db, obj_in=obj_in)
        for idx, q in enumerate(questions):
            quiz_service.add_question_to_quiz(db, quiz_id=q_assignment.id, question_id=q.id, question_order=idx + 1, marks=q.default_marks)
        seeded.append(q_assignment)
    else:
        seeded.append(existing_assignment)

    return seeded
