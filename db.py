from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:7416501516@localhost:5432/not_hackernews"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session.

    Yields:
        Session: A SQLAlchemy database session. Ensures the session is closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
