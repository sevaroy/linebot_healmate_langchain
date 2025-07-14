"""SQLAlchemy models for the application."""

from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

class MoodEntry(Base):
    __tablename__ = "mood_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    mood = Column(String, nullable=False)
    intensity = Column(Integer, nullable=True) # 1-10
    note = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True) # Store as JSONB for list of strings
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<MoodEntry(user_id='{self.user_id}', mood='{self.mood}', intensity={self.intensity})>"
