import os

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
DB_PATH = os.getenv("REVIEWS_DB_PATH", "reviews.db")
DEFAULT_PERSONA = os.getenv("DEFAULT_PERSONA", "mentor")
MOCK_LLM = os.getenv("MOCK_LLM", "true").lower() in ("1", "true", "yes")
