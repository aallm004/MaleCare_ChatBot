import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CLINICALTRIALS_API_BASE: str = os.getenv("CLINICALTRIALS_API_BASE", "https://clinicaltrials.gov/api/v2")

settings = Settings()