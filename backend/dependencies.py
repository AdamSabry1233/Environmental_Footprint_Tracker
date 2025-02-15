from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

#Set up database engine and session maker
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#Test connection when FASTAPI starts
try:
    with engine.connect() as connection:
        print("Successfully connected to PostgreSQL!")
except Exception as e:
    print("Connection failed:", e) 

# Dependancy to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()