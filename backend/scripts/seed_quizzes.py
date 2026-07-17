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

    return seeded
