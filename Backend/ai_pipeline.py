import os
from gtts import gTTS
import logging
from dotenv import load_dotenv

load_dotenv()

# Use the same DATA_DIR as main.py so audio lands on the persistent volume
_data_dir = os.getenv("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(_data_dir, "audio")

logger = logging.getLogger(__name__)

# Global variables to hold the HF pipelines (lazy-loaded)
_summarizer = None
_classifier = None

def get_summarizer():
    global _summarizer
    if _summarizer is None:
        from transformers import pipeline
        logger.info("Loading summarizer model (sshleifer/distilbart-cnn-12-6)...")
        _summarizer = pipeline(
            "summarization",
            model="sshleifer/distilbart-cnn-12-6",
            device="cpu",
            truncation=True,
        )
    return _summarizer

def get_classifier():
    global _classifier
    if _classifier is None:
        from transformers import pipeline
        logger.info("Loading zero-shot classification model (facebook/bart-large-mnli)...")
        _classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device="cpu",
        )
    return _classifier

def score_priority(title: str, summary: str) -> float:
    """
    Uses a local zero-shot classification SLM to score an article's newsworthiness.
    Returns a float between 0.0 (low priority) and 1.0 (critical/breaking).
    """
    try:
        classifier = get_classifier()
        text = f"{title}. {summary[:200]}"
        
        candidate_labels = [
            "breaking news crisis emergency",
            "important significant political economic",
            "routine local minor entertainment lifestyle"
        ]
        
        result = classifier(text, candidate_labels)
        
        # Map confidence scores: breaking=1.0, important=0.6, routine=0.2
        weights = {
            "breaking news crisis emergency": 1.0,
            "important significant political economic": 0.6,
            "routine local minor entertainment lifestyle": 0.2
        }
        
        # The top label gets the highest weight, scaled by its confidence
        score = 0.0
        for label, confidence in zip(result['labels'], result['scores']):
            score += weights.get(label, 0.3) * confidence
        
        return round(min(score, 1.0), 3)
    except Exception as e:
        logger.error(f"Failed to score priority: {str(e)}")
        return 0.3  # default medium-low

def summarize_article(text: str, max_sentences: int = 4, title: str = "") -> str:
    """
    Summarizes an article using a local HuggingFace Small Language Model (SLM).
    Accepts an optional `title` that is prepended to the input so the model
    stays on-topic and produces more accurate, focused summaries.
    """
    if not text or len(text.strip()) < 50:
        return text

    # Prepend the headline so the model understands the article's subject
    if title:
        input_text = f"{title.strip()}. {text.strip()}"
    else:
        input_text = text.strip()

    # Truncate to the model's effective input window
    input_text = input_text[:3000]

    try:
        summarizer = get_summarizer()
        result = summarizer(input_text, max_length=160, min_length=40, do_sample=False, truncation=True)
        return result[0]['summary_text']
    except Exception as e:
        logger.error(f"Failed to summarize with SLM: {str(e)}")
        # Fallback: extractive summary using first N sentences
        sentences = text.split('. ')
        summary = '. '.join(sentences[:max_sentences])
        if not summary.endswith('.'):
            summary += '.'
        return summary.strip()

def generate_daily_summary(articles: list, date_str: str) -> str:
    """
    Generates a 5-6 sentence summary of the day's high-priority current events.
    Prioritizes World, Politics, and Business for current affairs context.
    """
    if not articles:
        return "No significant news events were recorded today."
        
    intro = f"Welcome to your DailyNews AI briefing for {date_str}. Here are the most important current affairs you need to know today. "
    
    # Filter high priority categories first
    priority_categories = ["World", "Politics", "Business"]
    high_priority_articles = [a for a in articles if a.category in priority_categories]
    
    # Fallback to general articles if no high priority ones exist (unlikely)
    top_articles = high_priority_articles if high_priority_articles else articles
    
    # Take the absolute top 5 most recent/important
    top_headlines = [a.title for a in top_articles[:5]]
    
    body_texts = []
    if len(top_headlines) > 0:
        body_texts.append(f"In top news: {top_headlines[0]}.")
    if len(top_headlines) > 1:
        body_texts.append(f"Additionally, {top_headlines[1]}.")
    if len(top_headlines) > 2:
        body_texts.append(f"In geopolitical developments, {top_headlines[2]}.")
    if len(top_headlines) > 3:
        body_texts.append(f"On the global stage, {top_headlines[3]}.")
    if len(top_headlines) > 4:
        body_texts.append(f"And finally, {top_headlines[4]}.")
        
    summary_text = intro + " ".join(body_texts) + " That wraps up today's most crucial headlines."
    return summary_text


def generate_location_brief(articles: list, location_label: str) -> str:
    """
    Generates a short, conversational AI briefing paragraph.
    Combines the most relevant headlines provided into a 3–5 sentence narrative.
    """
    if not articles:
        return f"No news stories were found for your briefing right now. Check back in 30 minutes as the scraper refreshes regularly."

    from datetime import datetime
    now = datetime.now()
    time_greeting = (
        "Good morning" if now.hour < 12
        else "Good afternoon" if now.hour < 17
        else "Good evening"
    )

    # Sort by priority score then take top 5
    sorted_articles = sorted(articles, key=lambda a: a.priority_score, reverse=True)[:5]
    headlines = [a.title for a in sorted_articles]
    sources   = list({a.source for a in sorted_articles})[:3]

    # Build a natural-language briefing paragraph
    parts = [f"{time_greeting}. Here's your personalized briefing for {location_label}."]

    if len(headlines) >= 1:
        parts.append(f"The top story right now is: {headlines[0]}.")
    if len(headlines) >= 2:
        parts.append(f"Also making headlines: {headlines[1]}.")
    if len(headlines) >= 3:
        parts.append(f"In other significant news, {headlines[2]}.")
    if len(headlines) >= 4:
        parts.append(f"And additionally, {headlines[3]}.")
    if len(headlines) >= 5:
        parts.append(f"Finally, {headlines[4]}.")

    source_line = f"Sourced from {', '.join(sources)}." if sources else ""
    if source_line:
        parts.append(source_line)

    return " ".join(parts)


def text_to_speech(text: str, filename: str) -> str:
    """
    Converts text to speech and saves it as an MP3 file.
    Returns the relative URL path to the file.
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)
    filepath = os.path.join(AUDIO_DIR, f"{filename}.mp3")

    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)
        return f"/audio/{filename}.mp3"
    except Exception as e:
        logger.error(f"Error generating TTS: {str(e)}")
        return None
