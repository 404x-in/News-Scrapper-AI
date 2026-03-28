from apscheduler.schedulers.background import BackgroundScheduler
from scraper import fetch_and_process_news
import logging
import threading

logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 30 minutes
    scheduler.add_job(fetch_and_process_news, 'interval', minutes=30, id='fetch_news_job')
    scheduler.start()
    logger.info("Scheduler started. News will be fetched every 30 minutes.")

    # Trigger a fetch immediately on startup (in a background thread so the server starts fast)
    t = threading.Thread(target=fetch_and_process_news, daemon=True)
    t.start()
    logger.info("Initial news fetch triggered on startup.")
