import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    urls: list = [
        "https://www.holachamo.com",
        "https://www.paradigmadigital.com",
        "https://www.realpython.com",
        "https://www.lapatilla.com",
        "https://www.facebook.com",
        "https://www.gitlab.com",
        "https://www.youtube.com",
        "https://www.mozilla.org",
        "https://www.github.com",
        "https://www.google.com",
    ]
    pattern: str = r"href="
    api_stage: str = os.environ.get("API_STAGE", "")
