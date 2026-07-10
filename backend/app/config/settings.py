import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wechat_monitor.db")
    WECHAT_AUTH_STATE_PATH = os.getenv("WECHAT_AUTH_STATE_PATH", "./wechat_auth_state.json")
    DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./downloads")
    AI_API_BASE_URL = os.getenv("AI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1")
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    AI_MODEL = os.getenv("AI_MODEL", "gemini-3.5-flash")
    SYNC_INTERVAL_MINUTES = int(os.getenv("SYNC_INTERVAL_MINUTES", 60))

settings = Settings()
