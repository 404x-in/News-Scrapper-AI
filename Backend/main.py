import os
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

# Resolve persistent data directory (use DATA_DIR env var on Railway, else cwd)
DATA_DIR = os.getenv("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

from contextlib import asynccontextmanager
import models
import schemas
from database import engine, get_db
from scheduler import start_scheduler
import scraper
from scraper import fetch_district_news

# Create the database tables
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background job scheduler
    start_scheduler()
    yield
    # Shutdown logic if needed

app = FastAPI(title="DailyNews AI", lifespan=lifespan)

# CORS middleware — reads comma-separated origins from ALLOWED_ORIGINS env var
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure audio directory exists (uses absolute DATA_DIR path)
os.makedirs(AUDIO_DIR, exist_ok=True)
# Mount audio directory to serve static files
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

@app.get("/api/news", response_model=List[schemas.ArticleResponse])
def get_news(
    skip: int = 0, 
    limit: int = 20, 
    category: str = None, 
    search: str = None,
    db: Session = Depends(get_db)
):
    if search:
        # Dynamically fetch and store new articles for this search query globally
        scraper.fetch_search_results(search, db)

    query = db.query(models.Article)
    
    if category:
        query = query.filter(models.Article.category == category)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (models.Article.title.ilike(search_fmt)) | 
            (models.Article.summary.ilike(search_fmt))
        )
        
    articles = query.order_by(models.Article.published_at.desc()).offset(skip).limit(limit).all()
    return articles

@app.get("/api/daily-summary", response_model=schemas.DailySummaryResponse)
def get_daily_summary(db: Session = Depends(get_db)):
    # Get the latest daily summary
    summary = db.query(models.DailySummary).order_by(models.DailySummary.id.desc()).first()
    if not summary:
        raise HTTPException(status_code=404, detail="No daily summary found")
    return summary

@app.get("/api/top-news", response_model=List[schemas.ArticleResponse])
def get_top_news(
    limit: int = 8,
    db: Session = Depends(get_db)
):
    """Returns the most important articles sorted by SLM priority score."""
    articles = db.query(models.Article).order_by(
        models.Article.priority_score.desc(),
        models.Article.published_at.desc()
    ).limit(limit).all()
    return articles


def _keyword_match(article: models.Article, keywords: List[str]) -> bool:
    """Return True if any keyword appears in the article title or summary (case-insensitive)."""
    text = f"{article.title} {article.summary or ''}".lower()
    return any(kw.lower() in text for kw in keywords if kw)


def _tag_match(article: models.Article, tag: Optional[str]) -> bool:
    """Return True if the article's location_tag exactly matches the given tag (case-insensitive)."""
    if not tag or not article.location_tag:
        return False
    return article.location_tag.lower() == tag.lower()


@app.get("/api/briefing", response_model=schemas.BriefingResponse)
def get_briefing(
    city: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    section_limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
):
    """
    Returns a geo-hierarchical news briefing.
    Articles are pulled from the last 48 h. For city/state tiers we first
    look for articles with an exact location_tag match, then fall back to
    keyword search. District news is fetched on-demand via Google News RSS.
    """
    from datetime import datetime, timedelta

    # On-demand district fetch — fires quickly, tagged with location_tag=district
    if district and state:
        fetch_district_news(district, state, db)

    cutoff = datetime.utcnow() - timedelta(hours=48)
    all_articles: List[models.Article] = (
        db.query(models.Article)
        .filter(models.Article.published_at >= cutoff)
        .order_by(models.Article.priority_score.desc(), models.Article.published_at.desc())
        .limit(400)
        .all()
    )

    used_ids: set = set()

    def pick(
        keywords: List[str],
        exclude_categories: List[str] = [],
        only_categories: List[str] = [],
        location_tag: Optional[str] = None,
    ) -> List[models.Article]:
        results = []
        # Pass 1: exact location_tag match (city/state tagged articles)
        if location_tag:
            for a in all_articles:
                if a.id in used_ids:
                    continue
                if only_categories and a.category not in only_categories:
                    continue
                if exclude_categories and a.category in exclude_categories:
                    continue
                if _tag_match(a, location_tag):
                    results.append(a)
                if len(results) >= section_limit:
                    break
        # Pass 2: keyword fallback if tag-match didn't fill the section
        if len(results) < section_limit:
            for a in all_articles:
                if a.id in used_ids or a in results:
                    continue
                if only_categories and a.category not in only_categories:
                    continue
                if exclude_categories and a.category in exclude_categories:
                    continue
                if not keywords or _keyword_match(a, keywords):
                    results.append(a)
                if len(results) >= section_limit:
                    break
        for a in results:
            used_ids.add(a.id)
        return results

    sections: List[schemas.BriefingSection] = []

    # 1. City — prefer location_tag match, fallback to keyword
    if city:
        city_articles = pick([city], location_tag=city)
        if city_articles:
            sections.append(schemas.BriefingSection(
                label=f"City: {city}", emoji="🏘️", articles=city_articles
            ))

    # 2. District — location_tag set by on-demand fetch above
    if district:
        district_articles = pick([district], location_tag=district)
        if district_articles:
            sections.append(schemas.BriefingSection(
                label=f"District: {district}", emoji="🗺️", articles=district_articles
            ))

    # 3. State — prefer location_tag match, fallback to keyword
    if state:
        state_articles = pick([state], location_tag=state)
        if state_articles:
            sections.append(schemas.BriefingSection(
                label=f"State: {state}", emoji="🏛️", articles=state_articles
            ))

    # 4. National — prefer location_tag="India", fallback keyword match
    national_keywords = ["India", "Indian", "Modi", "Delhi", "Parliament", "Supreme Court"]
    if state:
        national_keywords.append(state)
    national_articles = pick(
        national_keywords,
        only_categories=["India", "Politics", "Business", "Science", "Technology", "Sports", "Entertainment", "Local"],
        location_tag="India",
    )
    if not national_articles:
        national_articles = pick([], only_categories=["India"])
    if national_articles:
        sections.append(schemas.BriefingSection(
            label="National", emoji="🇮🇳", articles=national_articles
        ))

    # 5. International — World category, non-India focus
    intl_articles = pick([], only_categories=["World"])
    if intl_articles:
        sections.append(schemas.BriefingSection(
            label="International", emoji="🌍", articles=intl_articles
        ))

    from ai_pipeline import generate_location_brief, text_to_speech

    # Build location label for the brief narrative
    location_parts = [p for p in [city, district, state] if p]
    location_label = ", ".join(location_parts) if location_parts else (country or "your region")

    # Collect all location-relevant articles (city + district + state + national + international)
    all_articles = []
    for s in sections:
        # Take up to 2 top articles from each section to give a comprehensive, multi-level overview
        all_articles.extend(s.articles[:2])

    local_summary = generate_location_brief(all_articles, location_label)

    audio_url = None
    if local_summary:
        import hashlib
        # Hash the summary text to act as a cache key for the audio file
        filename_hash = hashlib.md5(local_summary.encode()).hexdigest()
        audio_filename = f"briefing_{filename_hash}"
        # text_to_speech generates and saves the file, returning the URL path
        audio_url = text_to_speech(local_summary, audio_filename)

    return schemas.BriefingResponse(
        city=city,
        district=district,
        state=state,
        country=country,
        local_summary=local_summary,
        audio_url=audio_url,
        sections=sections,
    )
