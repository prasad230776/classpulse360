from fastapi import APIRouter
from app.api.v1.routers.auth import auth_router
from app.api.v1.routers.institution import institution_router
from app.api.v1.routers.question import question_router
from app.api.v1.routers.quiz import quiz_router
from app.api.v1.routers.session import session_router
from app.api.v1.routers.participant import participant_router
from app.api.v1.routers.subject import subject_router
from app.api.v1.routers.topic import topic_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
v1_router.include_router(institution_router, prefix="/institutions", tags=["Institutions"])
v1_router.include_router(question_router, prefix="/questions", tags=["Questions"])
v1_router.include_router(quiz_router, prefix="/quizzes", tags=["Quizzes"])
v1_router.include_router(session_router, prefix="/sessions", tags=["Sessions"])
v1_router.include_router(participant_router, prefix="/participants", tags=["Participants"])
v1_router.include_router(subject_router, prefix="/subjects", tags=["Subjects"])
v1_router.include_router(topic_router, prefix="/topics", tags=["Topics"])
