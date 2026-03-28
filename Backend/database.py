import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Use DATA_DIR env var (set on Railway to the persistent volume mount path)
# Falls back to the backend directory itself for local dev
_data_dir = os.getenv("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(_data_dir, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(_data_dir, 'news.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
