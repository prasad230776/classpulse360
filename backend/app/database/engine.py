from sqlalchemy import create_engine
from app.core.config import settings

# Create database engine using SQLAlchemy
# pool_pre_ping=True recycling stale connections automatically (critical for remote Supabase connections)
engine = create_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "development" else False,
    pool_pre_ping=True,
)
