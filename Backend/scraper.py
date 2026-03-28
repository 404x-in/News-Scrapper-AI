import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from ai_pipeline import summarize_article, generate_daily_summary, text_to_speech, score_priority
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Tier 5 — International / Category feeds (location_tag = None)
# ─────────────────────────────────────────────────────────────
RSS_FEEDS = {
    "Technology": [
        "https://www.theverge.com/rss/index.xml",                           # The Verge
        "http://feeds.bbci.co.uk/news/technology/rss.xml",                  # BBC Tech
        "https://timesofindia.indiatimes.com/rssfeeds/66946927.cms",        # TOI Tech
        "https://feeds.wired.com/wired/index",                              # Wired
        "https://techcrunch.com/feed/",                                     # TechCrunch
    ],
    "World": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",                      # BBC World
        "https://feeds.reuters.com/reuters/topNews",                        # Reuters Top News
        "https://www.aljazeera.com/xml/rss/all.xml",                        # Al Jazeera
        "https://www.theguardian.com/world/rss",                            # The Guardian World
        "https://rsshub.app/ap/topics/apf-topnews",                         # AP Top News
        "http://rss.cnn.com/rss/edition.rss",                               # CNN
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",        # NY Times
        "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",       # TOI World
    ],
    "Business": [
        "http://feeds.bbci.co.uk/news/business/rss.xml",                    # BBC Business
        "https://www.livemint.com/rss/news",                                # Mint
        "https://www.business-standard.com/rss/home_page_top_stories.rss",  # Business Standard
        "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",         # TOI Business
        "https://www.thehindu.com/business/feeder/default.rss",             # The Hindu Business
    ],
    "Science": [
        "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",     # BBC Science
        "https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms",     # TOI Science
        "https://www.theguardian.com/science/rss",                          # Guardian Science
    ],
    "Politics": [
        "http://feeds.bbci.co.uk/news/politics/rss.xml",                    # BBC Politics
        "https://www.thehindu.com/news/national/feeder/default.rss",        # The Hindu National
        "https://feeds.feedburner.com/ndtvnews-india-news",                 # NDTV India
        "https://feeds.washingtonpost.com/rss/national",                    # Washington Post
        "https://feeds.npr.org/1001/rss.xml",                               # NPR News
        "https://theprint.in/feed/",                                        # The Print
        "https://thewire.in/rss",                                           # The Wire
    ],
    "Entertainment": [
        "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",      # BBC Entertainment
        "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",      # TOI Entertainment
    ],
    "Sports": [
        "http://feeds.bbci.co.uk/sport/rss.xml",                            # BBC Sport
        "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",         # TOI Sports
    ],
    "India": [
        "https://www.thehindu.com/feeder/default.rss",                      # The Hindu (general)
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",       # TOI Top Stories
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",  # Hindustan Times
        "https://feeds.feedburner.com/ndtvnews-top-stories",                # NDTV Top Stories
        "https://indianexpress.com/feed/",                                  # Indian Express
        "https://www.indiatoday.in/rss/home",                               # India Today
        "https://scroll.in/rss",                                            # Scroll.in
        "https://www.news18.com/rss/india.xml",                             # News18
    ],
}

# ─────────────────────────────────────────────────────────────
# Tier 4 — National India extra (location_tag = "India")
# PIB + Doordarshan + Sansad TV press feeds
# ─────────────────────────────────────────────────────────────
NATIONAL_EXTRA_FEEDS = [
    # ✓ Verified working direct feeds
    "https://economictimes.indiatimes.com/rssfeedstopstories.cms",  # Economic Times
    "https://www.thehindu.com/news/national/feeder/default.rss",    # The Hindu National
    # Google News RSS — India national governance/policy topics
    "https://news.google.com/rss/search?q=PIB+India+government+press+release&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=Indian+Parliament+Lok+Sabha+Rajya+Sabha&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=India+Supreme+Court+High+Court+judgment&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=India+Budget+economy+RBI+policy&hl=en-IN&gl=IN&ceid=IN:en",
]

# ─────────────────────────────────────────────────────────────
# Tier 3 — State-level feeds  (location_tag = state name)
# ─────────────────────────────────────────────────────────────
INDIAN_STATE_FEEDS: dict[str, list[str]] = {
    # ─── States with verified working direct feeds ─────────────────────────
    "Maharashtra": [
        "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms",         # ✓ TOI Maharashtra
        "https://www.thehindu.com/news/national/other-states/feeder/default.rss",  # ✓ The Hindu
        "https://news.google.com/rss/search?q=Maharashtra+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Karnataka": [
        "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",         # ✓ TOI Karnataka
        "https://news.google.com/rss/search?q=Karnataka+Bengaluru+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Tamil Nadu": [
        "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",  # ✓ The Hindu TN
        "https://news.google.com/rss/search?q=Tamil+Nadu+Chennai+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Andhra Pradesh": [
        "https://www.deccanchronicle.com/rss.xml",                          # ✓ Deccan Chronicle
        "https://news.google.com/rss/search?q=Andhra+Pradesh+Vijayawada+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Telangana": [
        "https://www.deccanchronicle.com/rss.xml",                          # ✓ Deccan Chronicle (covers Telangana)
        "https://news.google.com/rss/search?q=Telangana+Hyderabad+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Assam": [
        "https://www.sentinelassam.com/feed/",                              # ✓ Sentinel Assam
        "https://news.google.com/rss/search?q=Assam+Guwahati+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Delhi": [
        "https://www.thehindu.com/news/cities/Delhi/feeder/default.rss",    # ✓ The Hindu Delhi
        "https://news.google.com/rss/search?q=Delhi+NCR+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    # ─── States using Google News RSS as primary source ──────────────────────
    "Kerala": [
        "https://news.google.com/rss/search?q=Kerala+Kochi+Thiruvananthapuram+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "West Bengal": [
        "https://news.google.com/rss/search?q=West+Bengal+Kolkata+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Gujarat": [
        "https://news.google.com/rss/search?q=Gujarat+Ahmedabad+Surat+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Rajasthan": [
        "https://news.google.com/rss/search?q=Rajasthan+Jaipur+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Uttar Pradesh": [
        "https://news.google.com/rss/search?q=Uttar+Pradesh+Lucknow+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Punjab": [
        "https://news.google.com/rss/search?q=Punjab+Chandigarh+Amritsar+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Haryana": [
        "https://news.google.com/rss/search?q=Haryana+Gurugram+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Odisha": [
        "https://news.google.com/rss/search?q=Odisha+Bhubaneswar+Cuttack+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Madhya Pradesh": [
        "https://news.google.com/rss/search?q=Madhya+Pradesh+Bhopal+Indore+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Bihar": [
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",  # ✓ HT India (covers Bihar)
        "https://news.google.com/rss/search?q=Bihar+Patna+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Goa": [
        "https://news.google.com/rss/search?q=Goa+Panaji+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Jharkhand": [
        "https://news.google.com/rss/search?q=Jharkhand+Ranchi+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Chhattisgarh": [
        "https://news.google.com/rss/search?q=Chhattisgarh+Raipur+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Uttarakhand": [
        "https://news.google.com/rss/search?q=Uttarakhand+Dehradun+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Himachal Pradesh": [
        "https://news.google.com/rss/search?q=Himachal+Pradesh+Shimla+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Jammu and Kashmir": [
        "https://news.google.com/rss/search?q=Jammu+Kashmir+Srinagar+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Manipur": [
        "https://news.google.com/rss/search?q=Manipur+Imphal+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Tripura": [
        "https://news.google.com/rss/search?q=Tripura+Agartala+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Meghalaya": [
        "https://news.google.com/rss/search?q=Meghalaya+Shillong+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
}

# ─────────────────────────────────────────────────────────────
# Tier 1+2 — City-specific feeds  (location_tag = city name)
# ─────────────────────────────────────────────────────────────
INDIAN_CITY_FEEDS: dict[str, list[str]] = {
    # ─── Verified working direct feeds + Google News RSS ──────────────────────
    "Mumbai": [
        "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms",         # ✓ TOI Mumbai
        "https://news.google.com/rss/search?q=Mumbai+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Delhi": [
        "https://www.thehindu.com/news/cities/Delhi/feeder/default.rss",    # ✓ The Hindu Delhi
        "https://news.google.com/rss/search?q=Delhi+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Bengaluru": [
        "https://timesofindia.indiatimes.com/rssfeeds/2647163.cms",         # ✓ TOI Bengaluru
        "https://www.thehindu.com/news/cities/bangalore/feeder/default.rss",# ✓ The Hindu Bengaluru
        "https://news.google.com/rss/search?q=Bengaluru+Bangalore+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Bangalore": [  # alias accepted from Nominatim
        "https://timesofindia.indiatimes.com/rssfeeds/2647163.cms",
        "https://www.thehindu.com/news/cities/bangalore/feeder/default.rss",
        "https://news.google.com/rss/search?q=Bengaluru+Bangalore+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Chennai": [
        "https://timesofindia.indiatimes.com/rssfeeds/2647163.cms",         # ✓ TOI Chennai
        "https://www.thehindu.com/news/cities/chennai/feeder/default.rss",  # ✓ The Hindu Chennai
        "https://news.google.com/rss/search?q=Chennai+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Hyderabad": [
        "https://www.deccanchronicle.com/rss.xml",                          # ✓ Deccan Chronicle
        "https://news.google.com/rss/search?q=Hyderabad+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Kolkata": [
        "https://timesofindia.indiatimes.com/rssfeeds/2647163.cms",         # ✓ TOI Kolkata
        "https://news.google.com/rss/search?q=Kolkata+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Pune": [
        "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms",         # ✓ TOI Pune/Maharashtra
        "https://news.google.com/rss/search?q=Pune+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Ahmedabad": [
        "https://news.google.com/rss/search?q=Ahmedabad+Gujarat+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Jaipur": [
        "https://news.google.com/rss/search?q=Jaipur+Rajasthan+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Lucknow": [
        "https://news.google.com/rss/search?q=Lucknow+Uttar+Pradesh+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Chandigarh": [
        "https://news.google.com/rss/search?q=Chandigarh+Punjab+Haryana+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Bhubaneswar": [
        "https://news.google.com/rss/search?q=Bhubaneswar+Odisha+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Guwahati": [
        "https://www.sentinelassam.com/feed/",                              # ✓ Sentinel Assam
        "https://news.google.com/rss/search?q=Guwahati+Assam+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Nagpur": [
        "https://timesofindia.indiatimes.com/rssfeeds/3908999.cms",         # ✓ TOI Maharashtra
        "https://news.google.com/rss/search?q=Nagpur+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Coimbatore": [
        "https://news.google.com/rss/search?q=Coimbatore+Tamil+Nadu+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Kochi": [
        "https://news.google.com/rss/search?q=Kochi+Kerala+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Thiruvananthapuram": [
        "https://news.google.com/rss/search?q=Thiruvananthapuram+Kerala+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Patna": [
        "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",  # ✓ HT India
        "https://news.google.com/rss/search?q=Patna+Bihar+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Bhopal": [
        "https://news.google.com/rss/search?q=Bhopal+Madhya+Pradesh+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Indore": [
        "https://news.google.com/rss/search?q=Indore+Madhya+Pradesh+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Surat": [
        "https://news.google.com/rss/search?q=Surat+Gujarat+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Visakhapatnam": [
        "https://news.google.com/rss/search?q=Visakhapatnam+Andhra+Pradesh+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
    "Amritsar": [
        "https://news.google.com/rss/search?q=Amritsar+Punjab+news&hl=en-IN&gl=IN&ceid=IN:en",
    ],
}


# Common browser user-agent to avoid 403/block responses
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def extract_content(url: str) -> str:
    """
    Extract main article text from a URL.
    Prefers <article>, <main>, or <div role='main'> containers
    before falling back to all <p> tags.
    """
    try:
        response = requests.get(url, timeout=10, headers=_HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove boilerplate elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        # Try to find the article body in common containers
        article_body = (
            soup.find("article")
            or soup.find("main")
            or soup.find(attrs={"role": "main"})
            or soup.find("div", class_=lambda c: c and any(
                kw in c.lower() for kw in ["article", "story", "content", "post-body"]
            ))
        )

        container = article_body if article_body else soup
        paragraphs = container.find_all('p')
        text = ' '.join(p.get_text(separator=' ', strip=True) for p in paragraphs)

        # Limit to first 3000 chars for the summarizer
        return text[:3000]
    except Exception as e:
        logger.error(f"Failed to extract {url}: {str(e)}")
        return ""


def _save_article(entry, category: str, source_title: str, location_tag: str | None, db: Session):
    """
    Parse a single feed entry, extract/summarize its content, and save to DB.
    Returns True if a new article was added.
    """
    exists = db.query(models.Article).filter(models.Article.url == entry.link).first()
    if exists:
        return False

    content = extract_content(entry.link)
    if not content or len(content.strip()) < 50:
        content = getattr(entry, 'summary', '')

    clean_content = BeautifulSoup(content, 'html.parser').get_text()
    if not clean_content:
        return False

    summary = summarize_article(clean_content, title=entry.title)

    image_url = None
    if hasattr(entry, 'media_thumbnail') and len(entry.media_thumbnail) > 0:
        image_url = entry.media_thumbnail[0]['url']
    elif hasattr(entry, 'media_content') and len(entry.media_content) > 0:
        image_url = entry.media_content[0]['url']

    if not image_url and '<img' in getattr(entry, 'summary', ''):
        img_soup = BeautifulSoup(entry.summary, 'html.parser')
        img_tag = img_soup.find('img')
        if img_tag and img_tag.get('src'):
            image_url = img_tag.get('src')

    published_at = datetime.utcnow()
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        published_at = datetime(*entry.published_parsed[:6])

    article = models.Article(
        title=entry.title,
        source=entry.get('source', {}).get('title', source_title),
        url=entry.link,
        category=category,
        summary=summary,
        image_url=image_url,
        priority_score=score_priority(entry.title, summary),
        location_tag=location_tag,
        published_at=published_at,
    )
    try:
        db.add(article)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving article {entry.link}: {str(e)}")
        db.rollback()
        return False


def fetch_search_results(query: str, db: Session):
    """
    Dynamically fetches news for a specific search query using Google News RSS.
    """
    logger.info(f"Dynamically fetching search results for: {query}")
    import urllib.parse
    search_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"

    try:
        feed = feedparser.parse(search_url)

        # Take top 5 results to keep the synchronous API response fast
        for entry in feed.entries[:5]:
            _save_article(entry, "Search", "Google News Search", None, db)

    except Exception as e:
        logger.error(f"Failed to hook up dynamic search feed for {query}: {str(e)}")


def fetch_district_news(district: str, state: str, db: Session):
    """
    Dynamically fetches district-level news via Google News RSS and tags
    articles with location_tag = district, category = "Local".
    Called on-demand by the /api/briefing endpoint.
    """
    logger.info(f"Fetching district news for: {district}, {state}")
    import urllib.parse
    query = f"{district} {state}"
    search_url = (
        f"https://news.google.com/rss/search?"
        f"q={urllib.parse.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
    )

    try:
        feed = feedparser.parse(search_url)
        for entry in feed.entries[:6]:
            _save_article(entry, "Local", "Google News", district, db)
    except Exception as e:
        logger.error(f"Failed to fetch district feed for {district}: {str(e)}")


def fetch_and_process_news():
    logger.info("Starting 30-minute news fetch...")
    db = SessionLocal()

    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    articles_fetched_today = []

    try:
        # ── Tier 5: Category / international feeds ──────────────────────────
        for category, feeds in RSS_FEEDS.items():
            for feed_url in feeds:
                logger.info(f"Fetching {category} from {feed_url}")
                try:
                    feed = feedparser.parse(feed_url)
                except Exception as e:
                    logger.error(f"Failed to parse feed {feed_url}: {str(e)}")
                    continue

                for entry in feed.entries[:3]:
                    added = _save_article(
                        entry, category,
                        feed.feed.get('title', 'Unknown Source'),
                        location_tag=None,
                        db=db
                    )
                    if added:
                        article = db.query(models.Article).filter(
                            models.Article.url == entry.link
                        ).first()
                        if article:
                            articles_fetched_today.append(article)

        # ── Tier 4: National India extra (PIB, DD, ET) ─────────────────────
        for feed_url in NATIONAL_EXTRA_FEEDS:
            logger.info(f"Fetching national extra from {feed_url}")
            try:
                feed = feedparser.parse(feed_url)
            except Exception as e:
                logger.error(f"Failed to parse national feed {feed_url}: {str(e)}")
                continue

            for entry in feed.entries[:3]:
                added = _save_article(
                    entry, "India",
                    feed.feed.get('title', 'National'),
                    location_tag="India",
                    db=db
                )
                if added:
                    article = db.query(models.Article).filter(
                        models.Article.url == entry.link
                    ).first()
                    if article:
                        articles_fetched_today.append(article)

        # ── Tier 3: State-level feeds ───────────────────────────────────────
        for state_name, feeds in INDIAN_STATE_FEEDS.items():
            for feed_url in feeds:
                logger.info(f"Fetching state '{state_name}' from {feed_url}")
                try:
                    feed = feedparser.parse(feed_url)
                except Exception as e:
                    logger.error(f"Failed to parse state feed {feed_url}: {str(e)}")
                    continue

                for entry in feed.entries[:2]:
                    added = _save_article(
                        entry, "Local",
                        feed.feed.get('title', state_name),
                        location_tag=state_name,
                        db=db
                    )
                    if added:
                        article = db.query(models.Article).filter(
                            models.Article.url == entry.link
                        ).first()
                        if article:
                            articles_fetched_today.append(article)

        # ── Tier 1+2: City-specific feeds ──────────────────────────────────
        for city_name, feeds in INDIAN_CITY_FEEDS.items():
            for feed_url in feeds:
                logger.info(f"Fetching city '{city_name}' from {feed_url}")
                try:
                    feed = feedparser.parse(feed_url)
                except Exception as e:
                    logger.error(f"Failed to parse city feed {feed_url}: {str(e)}")
                    continue

                for entry in feed.entries[:2]:
                    added = _save_article(
                        entry, "Local",
                        feed.feed.get('title', city_name),
                        location_tag=city_name,
                        db=db
                    )
                    if added:
                        article = db.query(models.Article).filter(
                            models.Article.url == entry.link
                        ).first()
                        if article:
                            articles_fetched_today.append(article)

        # ── Daily summary ───────────────────────────────────────────────────
        daily_summary = db.query(models.DailySummary).filter(
            models.DailySummary.date == today_str
        ).first()

        todays_articles = db.query(models.Article).filter(
            models.Article.created_at >= start_of_day
        ).all()

        if todays_articles and (not daily_summary or len(articles_fetched_today) > 0):
            logger.info("Generating daily summary and audio...")
            summary_text = generate_daily_summary(todays_articles, today_str)
            audio_path = text_to_speech(summary_text, f"daily_brief_{today_str}")

            if not daily_summary:
                daily_summary = models.DailySummary(
                    date=today_str,
                    summary_text=summary_text,
                    audio_file_path=audio_path
                )
                db.add(daily_summary)
            else:
                daily_summary.summary_text = summary_text
                daily_summary.audio_file_path = audio_path

            db.commit()

    except Exception as e:
        logger.error(f"Error in fetch pipeline: {str(e)}")
        db.rollback()
    finally:
        db.close()
        logger.info("Fetch pipeline completed.")


if __name__ == "__main__":
    fetch_and_process_news()
