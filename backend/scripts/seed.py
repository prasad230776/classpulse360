import sys
import os
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.helpers import SessionLocal, logger
from scripts.seed_institutions import seed_institutions
from scripts.seed_users import seed_users
from scripts.seed_subjects import seed_subjects
from scripts.seed_topics import seed_topics
from scripts.seed_questions import seed_questions
from scripts.seed_quizzes import seed_quizzes
from scripts.seed_sessions import seed_sessions


def main():
    parser = argparse.ArgumentParser(
        description="ClassPulse360 Modular Database Seeder"
    )
    parser.add_argument(
        "--all", action="store_true", help="Seed all datasets (Default)"
    )
    parser.add_argument(
        "--institutions", action="store_true", help="Seed institutions only"
    )
    parser.add_argument("--users", action="store_true", help="Seed users only")
    parser.add_argument(
        "--subjects", action="store_true", help="Seed subjects only"
    )
    parser.add_argument(
        "--topics", action="store_true", help="Seed topics only"
    )
    parser.add_argument(
        "--questions", action="store_true", help="Seed questions only"
    )
    parser.add_argument(
        "--quizzes", action="store_true", help="Seed quizzes only"
    )
    parser.add_argument(
        "--sessions",
        action="store_true",
        help="Seed sessions and activity logs only",
    )

    args = parser.parse_args()

    # Default to all if no arguments are passed
    if not (
        args.institutions
        or args.users
        or args.subjects
        or args.topics
        or args.questions
        or args.quizzes
        or args.sessions
    ):
        args.all = True

    db = SessionLocal()
    try:
        institutions = []
        users = {}
        subjects = {}
        topics = {}
        questions = []
        quizzes = []

        if args.all or args.institutions:
            institutions = seed_institutions(db)

        if args.all or args.users:
            if not institutions:
                institutions = seed_institutions(db)
            users = seed_users(db, institutions)

        if args.all or args.subjects:
            subjects = seed_subjects(db)

        if args.all or args.topics:
            if not subjects:
                subjects = seed_subjects(db)
            topics = seed_topics(db, subjects)

        if args.all or args.questions:
            if not subjects:
                subjects = seed_subjects(db)
            if not topics:
                topics = seed_topics(db, subjects)
            if not users:
                users = seed_users(db, seed_institutions(db))
            questions = seed_questions(db, topics, users)

        if args.all or args.quizzes:
            if not subjects:
                subjects = seed_subjects(db)
            if not topics:
                topics = seed_topics(db, subjects)
            if not users:
                users = seed_users(db, seed_institutions(db))
            if not questions:
                questions = seed_questions(db, topics, users)
            quizzes = seed_quizzes(db, questions, users)

        if args.all or args.sessions:
            if not subjects:
                subjects = seed_subjects(db)
            if not topics:
                topics = seed_topics(db, subjects)
            if not users:
                users = seed_users(db, seed_institutions(db))
            if not questions:
                questions = seed_questions(db, topics, users)
            if not quizzes:
                quizzes = seed_quizzes(db, questions, users)
            seed_sessions(db, quizzes, users)

        logger.info("Database Seeding Finished Successfully!")
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
