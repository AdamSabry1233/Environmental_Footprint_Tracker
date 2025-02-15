import os
from dotenv import load_dotenv

# Make sure to call the function
load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    API_KEY = os.getenv("API_KEY", "API KEY GOES HERE")

settings = Settings()
