import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


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


settings = Settings()
