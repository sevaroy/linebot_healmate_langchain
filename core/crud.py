"""CRUD (Create, Read, Update, Delete) operations for database models."""

from sqlalchemy.orm import Session
from . import models
from typing import List, Optional

def get_mood_entries_by_user(db: Session, user_id: str, limit: int = 5) -> List[models.MoodEntry]:
    """Fetches the most recent mood entries for a given user."""
    return db.query(models.MoodEntry).filter(models.MoodEntry.user_id == user_id).order_by(models.MoodEntry.timestamp.desc()).limit(limit).all()

def get_mood_summary_by_user(db: Session, user_id: str, days: int = 7) -> str:
    """Generates a summary of a user's mood over the last N days."""
    from datetime import datetime, timedelta
    from collections import Counter

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    mood_entries = db.query(models.MoodEntry).filter(
        models.MoodEntry.user_id == user_id,
        models.MoodEntry.timestamp >= start_date
    ).order_by(models.MoodEntry.timestamp.asc()).all()

    if not mood_entries:
        return f"過去 {days} 天沒有心情紀錄。"

    mood_counts = Counter(entry.mood for entry in mood_entries)
    total_entries = len(mood_entries)

    summary_parts = []
    for mood, count in mood_counts.most_common():
        percentage = (count / total_entries) * 100
        summary_parts.append(f"{mood} ({percentage:.1f}%)")
    
    mood_summary = f"過去 {days} 天的心情分佈：{', '.join(summary_parts)}。"

    # Add recent mood trend
    recent_mood = mood_entries[-1]
    trend_summary = f"最近一次紀錄是 {recent_mood.timestamp.strftime('%Y-%m-%d %H:%M')} 的 {recent_mood.mood} (強度: {recent_mood.intensity if recent_mood.intensity else 'N/A'})。"

    return f"{mood_summary} {trend_summary}"

