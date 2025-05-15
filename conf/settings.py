import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    urls: List[str] = [
        "https://go.dev",
        "https://www.python.org",
        "https://www.realpython.com",
        "https://www.instagram.com",
        "https://www.facebook.com",
        "https://www.gitlab.com",
        "https://www.youtube.com",
        "https://www.mozilla.org",
        "https://www.github.com",
        "https://www.google.com",
    ]
    pattern: str = r"href=\"(http|https)://"
    api_stage: str = os.environ.get("API_STAGE", "")
    cache_expire: int = 60  # Tiempo de caducidad de la caché en segundos
    cache_backend: str = "sqlite"  # Tipo de backend para la caché
    cache_db_path: str = ":memory:"  # Ruta para SQLite (en memoria por defecto)
    timeout: int = 10  # Timeout para las solicitudes HTTP en segundos

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Devuelve una instancia cacheada de la configuración
    """
    return Settings()
