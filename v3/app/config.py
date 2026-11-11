import sys
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure app package is discoverable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "book_tracker_v3"
    FIREBASE_CREDENTIALS_PATH: str = "./app/firebase/firebase-service-account.json"
    FIREBASE_WEB_API_KEY: Optional[str] = None
    # Automatically falls back to mock/offline mode when credentials file is missing
    USE_FIREBASE_MOCK: bool = False

    model_config = SettingsConfigDict(
        env_file=[str(BASE_DIR / ".env"), ".env"],
        extra="ignore"
    )

settings = Settings()

