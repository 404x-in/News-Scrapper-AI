from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from database import Base
import datetime

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    source = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    category = Column(String, index=True)
    summary = Column(Text)
    image_url = Column(String, nullable=True)
    priority_score = Column(Float, default=0.0, index=True)
    location_tag = Column(String, nullable=True, index=True)   # e.g. "Mumbai", "Maharashtra", "India", "World"
    published_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class DailySummary(Base):
    __tablename__ = "daily_summaries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, unique=True, index=True) # YYYY-MM-DD
    summary_text = Column(Text)
    audio_file_path = Column(String, nullable=True)
