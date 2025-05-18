import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    urls: List[str] = [
        "https://go.dev",
        "https://www.python.org",
        "https://www.realpython.com",
        "https://nodejs.org",
        "https://www.facebook.com",
        "https://www.gitlab.com",
        "https://www.youtube.com",
        "https://www.mozilla.org",
        "https://www.github.com",
        "https://www.google.com",
    ]
    pattern: str = r"href=\"(http|https)://"
    api_stage: str = os.environ.get("API_STAGE", "")
    cache_expire: int = 60  # Cache expiration time in seconds
    cache_backend: str = "sqlite"  # Cache backend type
    cache_db_path: str = ":memory:"  # Path for SQLite (in memory by default)
    timeout: int = 10  # Timeout for HTTP requests in seconds

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings
    """
    return Settings()
