from sqlalchemy.orm import Session
from scripts.helpers import logger
from scripts.seed_institutions import seed_institutions

from app.common.enums import UserRole
from app.schemas.user import UserCreate
from app.services.auth_service import auth_service
from app.repositories.user_repository import user_repository


def seed_users(db: Session, institutions: list) -> dict:
    """
    Seed admin, teacher, and student users idempotently.
    """
    logger.info("Seeding Users...")
    users_to_seed = [
        {
            "name": "Super Administrator",
            "username": "superadmin",
            "email": "superadmin@classpulse360.com",
            "password": "SuperAdminPassword123!",
            "role": UserRole.SUPER_ADMIN,
        },
        {
            "name": "System Administrator",
            "username": "admin",
            "email": "admin@classpulse360.com",
            "password": "AdminPassword123!",
            "role": UserRole.ADMIN,
        },
        {
            "name": "Dr. Sarah Jenkins",
            "username": "sjenkins",
            "email": "teacher@classpulse360.com",
            "password": "TeacherPassword123!",
            "role": UserRole.TEACHER,
        },
        {
            "name": "Alex Student",
            "username": "astudent",
            "email": "student@classpulse360.com",
            "password": "StudentPassword123!",
            "role": UserRole.STUDENT,
        },
    ]

    seeded = {}
    inst_id = institutions[0].id if institutions else None

    for user_data in users_to_seed:
        existing = user_repository.get_by_email(db, email=user_data["email"])
        if not existing:
            obj_in = UserCreate(
                name=user_data["name"],
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                role=user_data["role"],
                institution_id=inst_id,
            )
            new_user = auth_service.register(db, user_in=obj_in)
            logger.info(f"Registered User: {new_user.name} ({new_user.role.value})")
            seeded[user_data["role"]] = new_user
        else:
            logger.info(f"User {user_data['email']} already exists, skipping.")
            seeded[user_data["role"]] = existing

    return seeded
