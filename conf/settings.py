import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    random_website: list = [
        "https://www.lapatilla.com",
        "https://www.paradigmadigital.com",
        "https://www.realpython.com",
        "https://www.facebook.com",
        "https://www.instagram.com",
        "https://www.youtube.com",
        "https://www.mozilla.org",
        "https://www.github.com",
        "https://www.google.com",
        "https://www.holachamo.com"
    ]
    dir_download: str = "/tmp/download/"
    dir_counted: str = "/tmp/counted/"
    api_stage: str = os.environ.get("API_STAGE", "")
