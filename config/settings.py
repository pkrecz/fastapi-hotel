import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import ClassVar
from dotenv import load_dotenv
from functools import lru_cache


load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    title: str = "Hotel - booking"
    version: str = "1.0.0"
    docs_url: str = "/swagger"


    ACCESS_SECRET_KEY: str = str(os.getenv("ACCESS_SECRET_KEY"))
    REFRESH_SECRET_KEY: str = str(os.getenv("REFRESH_SECRET_KEY"))
    ALGORITHM: str = str(os.getenv("ALGORITHM"))
    FUTURE_PERIOD_IN_DAYS: str = str(os.getenv("FUTURE_PERIOD_IN_DAYS"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 240
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    MAIL_USERNAME: str = str(os.getenv("MAIL_USERNAME"))
    MAIL_PASSWORD: str = str(os.getenv("MAIL_PASSWORD"))
    MAIL_FROM: str = str(os.getenv("MAIL_FROM"))
    MAIL_PORT: int = int(os.getenv("MAIL_PORT"))
    MAIL_SERVER: str = str(os.getenv("MAIL_SERVER"))
    MAIL_FROM_NAME: str = str(os.getenv("MAIL_FROM_NAME"))
    MAIL_STARTTLS: bool = bool(os.getenv("MAIL_STARTTLS"))
    MAIL_SSL_TLS: bool = bool(os.getenv("MAIL_SSL_TLS"))
    USE_CREDENTIALS: bool = bool(os.getenv("USE_CREDENTIALS"))
    VALIDATE_CERTS: bool = bool(os.getenv("VALIDATE_CERTS"))
    TEMPLATE_FOLDER: ClassVar = Path(BASE_DIR, "util", "templates")
    LOG_FILES: ClassVar = Path(BASE_DIR, str(os.getenv("LOG_FILES")))


@lru_cache(maxsize=None, typed=False)
def get_settings():
    return Settings()

settings = get_settings()
