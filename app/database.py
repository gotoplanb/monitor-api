from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base
from app.models.monitor import Monitor, MonitorStatus, Tag  # Import the models

# Create engine with check_same_thread=False for SQLite
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)


# Initialize the database
init_db()
