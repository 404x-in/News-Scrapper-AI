from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    source: str
    url: str
    category: str
    summary: str
    image_url: Optional[str] = None
    priority_score: float = 0.0
    location_tag: Optional[str] = None
    published_at: datetime

class ArticleResponse(ArticleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DailySummaryBase(BaseModel):
    date: str
    summary_text: str
    audio_file_path: Optional[str] = None

class DailySummaryResponse(DailySummaryBase):
    id: int

    class Config:
        from_attributes = True

class BriefingSection(BaseModel):
    label: str           # e.g. "City: Mumbai", "State: Maharashtra"
    emoji: str           # e.g. "📍", "🏛️"
    articles: List[ArticleResponse]

class BriefingResponse(BaseModel):
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    local_summary: Optional[str] = None   # AI-generated location briefing paragraph
    audio_url: Optional[str] = None       # Path to generated TTS audio
    sections: List[BriefingSection]
