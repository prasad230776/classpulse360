from sqlalchemy.orm import Session
from scripts.helpers import logger

from app.common.enums import UserRole, DifficultyLevel, QuestionType
from app.schemas.question import QuestionCreate
from app.services.question_service import question_service
from app.repositories.question_repository import question_repository


def seed_questions(db: Session, topics: dict, users: dict) -> list:
    """
    Seed sample questions.
    """
    logger.info("Seeding Questions...")
    teacher = users.get(UserRole.TEACHER)
    teacher_id = teacher.id if teacher else None

    algebra_topic = topics.get("ALG")
    algebra_id = algebra_topic.id if algebra_topic else None

    mechanics_topic = topics.get("MEC")
    mechanics_id = mechanics_topic.id if mechanics_topic else None

    questions_to_seed = [
        {
            "topic_id": algebra_id,
            "question_text": "What is the value of x in the equation 2x + 5 = 15?",
            "question_type": QuestionType.MCQ_SINGLE,
            "options": {
                "choices": [
                    {"id": "a", "text": "5"},
                    {"id": "b", "text": "10"},
                    {"id": "c", "text": "15"},
                    {"id": "d", "text": "20"},
                ]
            },
            "correct_answer": {"id": "a"},
            "difficulty_level": DifficultyLevel.EASY,
            "default_marks": "1.00",
            "default_time_limit_seconds": 30,
        },
        {
            "topic_id": mechanics_id,
            "question_text": "True or False: Acceleration is a vector quantity.",
            "question_type": QuestionType.TRUE_FALSE,
            "options": {
                "choices": [
                    {"id": "t", "text": "True"},
                    {"id": "f", "text": "False"},
                ]
            },
            "correct_answer": {"id": "t"},
            "difficulty_level": DifficultyLevel.EASY,
            "default_marks": "1.00",
            "default_time_limit_seconds": 20,
        },
    ]

    seeded = []
    for q_data in questions_to_seed:
        if not q_data["topic_id"] or not teacher_id:
            continue
        existing = (
            db.query(question_repository.model)
            .filter(
                question_repository.model.question_text == q_data["question_text"]
            )
            .first()
        )

        if not existing:
            obj_in = QuestionCreate(
                topic_id=q_data["topic_id"],
                created_by=teacher_id,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                difficulty_level=q_data["difficulty_level"],
                default_marks=q_data["default_marks"],
                default_time_limit_seconds=q_data["default_time_limit_seconds"],
            )
            new_q = question_service.create_question(db, obj_in=obj_in)
            logger.info(f"Created Question: {new_q.question_text[:50]}...")
            seeded.append(new_q)
        else:
            logger.info(
                f"Question '{q_data['question_text'][:30]}...' already exists, skipping."
            )
            seeded.append(existing)

    return seeded
