# config.py — add to your existing file
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing from .env")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-5.4-mini")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
