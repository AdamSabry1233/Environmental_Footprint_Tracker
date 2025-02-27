import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .config import settings  # Assuming you have a config module
from pathlib import Path

# Base Class for ORM Models
Base = declarative_base()

target_metadata = Base.metadata

# Automatically find and load .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL") or settings.DATABASE_URL

# SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db  # Provides a session for requests
    finally:
        db.close()

# Test connection when FastAPI starts
try:
    with engine.connect() as connection:
        print("✅ Successfully connected to PostgreSQL!")
except Exception as e:
    print("❌ Connection failed:", e)
