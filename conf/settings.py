import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    urls: List[str] = [
        "https://go.dev", "https://www.python.org", "https://www.realpython.com",
        "https://nodejs.org", "https://www.facebook.com", "https://www.gitlab.com",
        "https://www.youtube.com", "https://www.mozilla.org", "https://www.github.com",
        "https://www.google.com"
    ]
    pattern: str = r"href=\"(http|https)://"
    api_stage: str = os.environ.get("API_STAGE", "")
    cache_expire: int = 60
    cache_backend: str = "sqlite"
    cache_db_path: str = os.environ.get("CACHE_DB_PATH", ":memory:")
    timeout: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
