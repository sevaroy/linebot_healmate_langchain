"""Database session management for the application."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Construct the database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('POSTGRES_USER', 'healmate')}:{os.getenv('POSTGRES_PASSWORD', 'healmate_pass')}@localhost:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'healmate_db')}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
