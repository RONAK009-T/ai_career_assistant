import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
CSS_DIR = STATIC_DIR / "css"
DATA_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

APP_NAME = "NexusAI Career and Productivity Assistant"
APP_VERSION = "2.0.0"
APP_TAGLINE = "All-in-One AI Career Acceleration and Intelligent Productivity Workspace"

# Database Configuration (MySQL / SQLite)
DB_ENGINE = os.getenv("DB_ENGINE", "mysql").lower()  # "mysql" or "sqlite"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_NAME = os.getenv("DB_NAME", "ai_career_assistant_db")
DB_SSL = os.getenv("DB_SSL", "auto").lower()  # "true", "false", or "auto"
DATABASE_PATH = DATA_DIR / "app.db"

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PRIMARY_MODEL = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.0-flash")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash")

MAX_FILE_SIZE_MB = 10
ALLOWED_RESUME_EXTENSIONS = [".pdf", ".docx", ".txt"]
ALLOWED_DOC_EXTENSIONS = [".pdf", ".txt", ".docx", ".md"]

THEME = {
    "bg_primary": "#0B0F17",
    "bg_secondary": "#111827",
    "bg_card": "rgba(17, 24, 39, 0.75)",
    "accent_emerald": "#10B981",
    "accent_cyan": "#06B6D4",
    "accent_violet": "#8B5CF6",
    "accent_amber": "#F59E0B",
    "accent_rose": "#EF4444",
    "text_primary": "#F9FAFB",
    "text_muted": "#9CA3AF",
    "border_glass": "rgba(255, 255, 255, 0.08)"
}
