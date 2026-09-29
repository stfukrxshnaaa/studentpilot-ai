"""
Configuration manager for StudyPilot AI.
Loads settings from environment variables and provides sensible defaults.
Never hardcodes sensitive keys.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load .env file from base directory if present
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Application metadata
APP_TITLE = "StudyPilot AI"
APP_SUBTITLE = "Your Intelligent College Study Copilot & Exam Strategist"
APP_VERSION = "1.0.0"
APP_ICON = "🚀"

# Database Configuration
DEFAULT_DB_PATH = DATA_DIR / "studypilot.db"
DB_PATH = Path(os.getenv("STUDYPILOT_DB_PATH", str(DEFAULT_DB_PATH)))
if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH

# LLM Providers Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower().strip()

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

# Pomodoro Defaults (in minutes)
DEFAULT_FOCUS_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15

def get_active_provider() -> str:
    """Returns the effective active provider based on availability of keys."""
    # Check explicitly requested provider first
    if LLM_PROVIDER == "gemini" and GEMINI_API_KEY:
        return "gemini"
    elif LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        return "openai"
    elif LLM_PROVIDER == "groq" and GROQ_API_KEY:
        return "groq"
    
    # Otherwise check any available key
    if GEMINI_API_KEY:
        return "gemini"
    if OPENAI_API_KEY:
        return "openai"
    if GROQ_API_KEY:
        return "groq"
    
    return "demo"

def has_live_llm() -> bool:
    """Returns True if any valid LLM API key is configured."""
    return get_active_provider() != "demo"
